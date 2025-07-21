import logging
from bs4 import BeautifulSoup
import requests
from typing import Literal, Any
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

def _sel_pubs(year: str = "near3") -> list[dict[str, Any]]:
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

def _pubs_dispatcher(notice: dict[str, Any]) -> list[dict[str, Any]]:
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

def _pubs_basic_frame(submit: dict[str, Any]) -> list[dict[str, Any]]:
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

def _pubstype_detail(subject: dict[str, Any]) -> list[dict[str, Any]]:
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

def fetch(year: str = "near3") -> list[dict[str, Any]]:
    """
    Fetch all publication data for the specified year.
    """
    logger.info(f"Starting fetch for year={year}")
    try:
        notices = _sel_pubs(year)
        submits = []
        for notice in notices:
            try:
                submits.extend(_pubs_dispatcher(notice))
            except Exception as e:
                logger.error(f"Error in fetch: _pubs_dispatcher failed | notice={notice} | {e}")
        logger.info(f"Total submits fetched: {len(submits)}")
        subjects = []
        for submit in submits:
            try:
                subjects.extend(_pubs_basic_frame(submit))
            except Exception as e:
                logger.error(f"Error in fetch: _pubs_basic_frame failed | submit={submit} | {e}")
        logger.info(f"Total subjects fetched: {len(subjects)}")
        accounts = []
        for subject in subjects:
            try:
                accounts.extend(_pubstype_detail(subject))
            except Exception as e:
                logger.error(f"Error in fetch: _pubstype_detail failed | subject={subject} | {e}")
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