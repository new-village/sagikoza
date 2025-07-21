from bs4 import BeautifulSoup
from typing import List, Dict

def parse_notices(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """
    BeautifulSoupオブジェクトからbutton.button_whiteまたはbutton.button_blueのテキスト内容と
    input[name='doc_id']のvalueを抽出し、リスト辞書形式で返す。

    Args:
        soup: BeautifulSoupオブジェクト

    Returns:
        List[Dict[str, str]]: 抽出結果のリスト。各要素は{'label': ボタンテキスト, 'doc_id': ドキュメントID}
    """
    notices: List[Dict[str, str]] = []

    # ボタン要素を取得
    buttons = soup.find_all('button', class_=['button_white', 'button_blue'])
    # 対応するinput[name='doc_id']を取得
    inputs = soup.find_all('input', attrs={'name': 'doc_id'})

    for btn, inp in zip(buttons, inputs):
        # ボタン内の文字列を結合
        label = ' '.join(btn.stripped_strings).replace('\u3000', ' ').strip()
        doc_id = inp.get('value', '')
        notices.append({'label': label, 'doc_id': doc_id})

    return notices