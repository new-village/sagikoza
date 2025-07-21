import logging
from bs4 import BeautifulSoup
import requests
from typing import Literal, Any, Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
from time import sleep
from sagikoza.parser.sel_pubs import parse_notices
from sagikoza.parser.pubs_dispatcher import parse_submit
from sagikoza.parser.pubs_basic_frame import parse_subject
from sagikoza.parser.pubstype_detail import parse_accounts

DOMAIN = "https://furikomesagi.dic.go.jp"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}
SESSION = requests.Session()
SESSION.trust_env = False

logger = logging.getLogger(__name__)

class FetchError(Exception):
    """Exception for HTML fetch errors."""
    pass

def retry_on_error(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry function calls on failure."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {e}")
                        sleep(delay * (2 ** attempt))  # Exponential backoff
                    else:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}")
            raise last_exception
        return wrapper
    return decorator

def process_items_with_error_handling(items: List[Dict[str, Any]], 
                                    processor_func: callable, 
                                    item_name: str,
                                    max_workers: int = 5) -> List[Dict[str, Any]]:
    """Process a list of items with error handling and logging using multithreading."""
    results = []
    successful = 0
    failed = 0
    
    if not items:
        logger.info(f"No {item_name}s to process")
        return results
    
    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_item = {executor.submit(processor_func, item): item for item in items}
        
        # Process completed tasks as they finish
        for future in as_completed(future_to_item):
            item = future_to_item[future]
            try:
                processed = future.result()
                results.extend(processed)
                successful += 1
                logger.debug(f"Successfully processed {item_name}: {item.get('doc_id', item.get('no', 'unknown'))}")
            except Exception as e:
                failed += 1
                logger.error(f"Error processing {item_name}: {item} | {e}")
    
    logger.info(f"Processed {len(items)} {item_name}s: {successful} successful, {failed} failed")
    return results

@retry_on_error(max_retries=3, delay=1.0)
def fetch_html(
    url: str,
    method: Literal['GET', 'POST'] = 'GET',
    data: dict | None = None,
    timeout: float = 5.0,
) -> BeautifulSoup:
    """
    Fetch HTML and return a BeautifulSoup object.

    Args:
        url: Target URL
        method: HTTP method ('GET' or 'POST')
        data: Parameters for GET or body for POST
        timeout: Request timeout (seconds)

    Raises:
        FetchError: On network, HTTP, or timeout errors
    """
    logger.info(f"Fetching HTML: url={url}, method={method}, data={data}")
    try:
        if method == 'GET':
            resp = SESSION.get(url, params=data, headers=HEADERS, timeout=timeout)
        else:
            resp = SESSION.post(url, data=data, headers=HEADERS, timeout=timeout)
            resp.encoding = resp.apparent_encoding
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f'Error fetching HTML from {url}: {e} | method={method} | data={data}')
        raise FetchError(f'Failed to fetch HTML from {url}') from e
    return BeautifulSoup(resp.text, 'html.parser')

def _sel_pubs(year: str = "near3") -> List[Dict[str, Any]]:
    """
    Get publication notices for the specified year.
    """
    logger.info(f"Getting publication notices for year={year}")
    url = f"{DOMAIN}/sel_pubs.php"
    payload = {
        "search_term": year,
        "search_no": "none",
        "search_pubs_type": "none",
        "sort_id": "5"
    }
    try:
        soup = fetch_html(url, "POST", payload)
        notices = parse_notices(soup)
        logger.info(f"Fetched {len(notices)} notices for year={year}")
        if not notices:
            logger.warning(f"No notices found for year={year}")
        return notices
    except Exception as e:
        logger.error(f"Exception in _sel_pubs: {e} | year={year}")
        raise

def _pubs_dispatcher(notice: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Get publication details for a notice.
    """
    logger.info(f"Getting publication details for notice doc_id={notice.get('doc_id')}")
    url = f"{DOMAIN}/pubs_dispatcher.php"
    payload = {"head_line": "", "doc_id": notice['doc_id']}
    try:
        soup = fetch_html(url, "POST", payload)
        details = parse_submit(soup)
        logger.info(f"Fetched {len(details)} details for doc_id={notice.get('doc_id')}")
        if not details:
            logger.warning(f"No details found for doc_id={notice.get('doc_id')}")
        return [{**detail, **notice} for detail in details]
    except Exception as e:
        logger.error(f"Exception in _pubs_dispatcher: {e} | notice={notice}")
        raise

def _pubs_basic_frame(submit: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Get basic publication information for a submit.
    """
    logger.info(f"Getting basic publication info for submit params={submit.get('params')}")
    url = f"{DOMAIN}/pubs_basic_frame.php"
    try:
        soup = fetch_html(url, "GET", submit['params'])
        details = parse_subject(soup)
        logger.info(f"Fetched {len(details)} subjects for submit params={submit.get('params')}")
        if not details:
            logger.warning(f"No subjects found for submit params={submit.get('params')}")
        return [{**detail, **submit} for detail in details]
    except Exception as e:
        logger.error(f"Exception in _pubs_basic_frame: {e} | submit={submit}")
        raise

def _pubstype_detail(subject: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Get account details for a subject.
    """
    logger.info(f"Getting account details for subject no={subject.get('no')}, form={subject.get('form')}")
    url = f"{DOMAIN}/" + subject['form']
    payload = {
        "r_no": subject['no'],
        "pn": subject.get('pn', ''),
        "p_id": subject.get('p_id', ''),
        "re": subject.get('re', ''),
        "referer": '0'
    }
    try:
        soup = fetch_html(url, "POST", payload)
        details = parse_accounts(soup)
        logger.info(f"Fetched {len(details)} accounts for subject no={subject.get('no')}")
        if not details:
            logger.warning(f"No accounts found for subject no={subject.get('no')}")
        return [{**detail, **subject} for detail in details]
    except Exception as e:
        logger.error(f"Exception in _pubstype_detail: {e} | subject={subject}")
        raise

def fetch(year: str = "near3", max_workers: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch all publication data for the specified year.
    
    Args:
        year: Year to fetch data for, or "near3" for latest 3 months
        max_workers: Maximum number of concurrent threads for parallel processing
    """
    logger.info(f"Starting fetch for year={year} with max_workers={max_workers}")
    try:
        # Step 1: Get notices
        notices = _sel_pubs(year)
        
        # Step 2: Get submits with error handling and parallel processing
        submits = process_items_with_error_handling(notices, _pubs_dispatcher, "notice", max_workers)
        logger.info(f"Total submits fetched: {len(submits)}")
        
        # Step 3: Get subjects with error handling and parallel processing
        subjects = process_items_with_error_handling(submits, _pubs_basic_frame, "submit", max_workers)
        logger.info(f"Total subjects fetched: {len(subjects)}")
        
        # Step 4: Get accounts with error handling and parallel processing
        accounts = process_items_with_error_handling(subjects, _pubstype_detail, "subject", max_workers)
        logger.info(f"Total accounts fetched: {len(accounts)}")
        
        logger.info(f"Fetch completed for year={year}")
        if not accounts:
            logger.warning(f"No accounts fetched for year={year}")
        return accounts
    except Exception as e:
        logger.error(f"Exception in fetch: {e} | year={year}")
        raise

if __name__ == "__main__":
    import pandas as pd
    df = pd.DataFrame(fetch())
    df.to_parquet("accounts.parquet", index=False)