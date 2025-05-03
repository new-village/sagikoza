import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse
import concurrent.futures

DOMAIN = "https://furikomesagi.dic.go.jp"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def _get_notice_table(search_term: str):
    """
    公告一覧テーブルを取得
    """
    url = f"{DOMAIN}/sel_pubs.php"
    payload = {
        "search_term": search_term,
        "search_no": "none",
        "search_pubs_type": "none",
        "sort_id": "5"
    }
    response = requests.post(url, data=payload, headers=HEADERS)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.find("table", class_="sel_pubs_list")

def _extract_doc_ids(table):
    """
    公告IDリストをテーブルから抽出
    """
    if not table:
        print("公告テーブルが見つかりませんでした。")
        return []
    doc_ids = [inp.get('value') for inp in table.find_all('input', {'name': 'doc_id'}) if inp.get('value')]
    # デバッグ用（14915 のみ抽出）
    return [doc_id for doc_id in doc_ids if doc_id.strip() == "14915"]

def _fetch_detail_html(doc_id: str):
    """
    公告詳細ページのHTMLを取得
    """
    url = f"{DOMAIN}/pubs_dispatcher.php"
    payload = {"head_line": "", "doc_id": doc_id}
    response = requests.post(url, data=payload, headers=HEADERS)
    response.encoding = response.apparent_encoding
    return BeautifulSoup(response.text, "html.parser")

def _get_basic_frame_links(detail_soup):
    """
    pubs_basic_frame.php へのリンクを抽出
    """
    return [link.get('href').replace('.', '', 1) for link in detail_soup.find_all('a')
            if link.get('href', '').startswith('./pubs_basic_frame.php')]

def _fetch_table_from_basic_frame(abs_link):
    """
    pubs_basic_frame.php のテーブルを取得
    """
    url = f"{DOMAIN}{abs_link}"
    response = requests.get(url, headers=HEADERS)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.find('table', style="{ border: 1px #333333 solid; width: 800px; border-collapse: collapse; empty-cells: show; }")

def _parse_table_rows(table, doc_id, abs_link):
    """
    テーブル行をパースして辞書リスト化
    """
    if not table:
        return []
    rows = table.find_all('tr')[2:]
    query_params = parse_qs(urlparse(abs_link).query)
    bank_code = query_params.get('inst_code', [None])[0]
    p_id = query_params.get('p_id', [None])[0]
    pn = query_params.get('pn', [None])[0]
    flat_links = []
    for row in rows:
        record = row.find_all('td')
        if len(record) == 7:
            id = record[0].find('input').get('value', None).strip() if record[0].find('input') else None
            process = record[0].find('a').text.strip() if record[0].find('a') else None
            bank_name = record[1].text.strip()
            flat_links.append({
                "doc_id": doc_id,
                "id": id,
                "p_id": p_id,
                "pn": pn,
                "process": process,
                "bank_name": bank_name,
                "bank_code": bank_code,
                "branch_name": record[2].text.strip(),
                "branch_code": record[3].text.strip(),
                "type": record[4].text.strip(),
                "account": record[5].text.strip(),
                "name": record[6].text.strip().replace('\u3000', ' '),
            })
        elif len(record) == 5:
            # ゆうちょ銀行などの例外処理
            flat_links.append({
                "doc_id": doc_id,
                "id": id,
                "p_id": p_id,
                "pn": pn,
                "process": process,
                "bank_name": bank_name,
                "bank_code": bank_code,
                "branch_name": record[0].text.strip(),
                "branch_code": record[1].text.strip(),
                "type": record[2].text.strip(),
                "account": record[3].text.strip(),
                "name": record[4].text.strip().replace('\u3000', ' '),
            })
    return flat_links

def _fetch_notices(search_term: str):
    """
    振り込め詐欺救済法に基づく公告を検索条件に基づいて取得する共通関数
    """
    table = _get_notice_table(search_term)
    doc_ids = _extract_doc_ids(table)
    flat_links = []
    def process_doc_id(doc_id):
        detail_soup = _fetch_detail_html(doc_id)
        abs_links = _get_basic_frame_links(detail_soup)
        results = []
        def process_abs_link(abs_link):
            table = _fetch_table_from_basic_frame(abs_link)
            return _parse_table_rows(table, doc_id, abs_link)
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as link_executor:
            link_futures = [link_executor.submit(process_abs_link, abs_link) for abs_link in abs_links]
            for future in concurrent.futures.as_completed(link_futures):
                try:
                    results.extend(future.result())
                except Exception:
                    continue
        return results
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as doc_executor:
        doc_futures = [doc_executor.submit(process_doc_id, doc_id) for doc_id in doc_ids]
        for future in concurrent.futures.as_completed(doc_futures):
            try:
                flat_links.extend(future.result())
            except Exception:
                continue
    return flat_links

def fetch(year: str = None):
    """
    指定した年(YYYY)または直近3ヶ月分の振り込め詐欺救済法に基づく公告を取得します。
    年が指定されていればその年の公告一覧を、指定されていなければ直近3ヶ月分を取得します。
    """
    if year is None:
        return _fetch_notices("near3")
    try:
        y = int(year)
        now_year = datetime.datetime.now().year
        if y < 2008 or y > now_year:
            raise ValueError("Year must be 2008 or later and not in the future.")
    except Exception as e:
        raise ValueError("Invalid year format. Use 'YYYY'.") from e
    return _fetch_notices(year)