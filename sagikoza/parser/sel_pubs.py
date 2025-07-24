from bs4 import BeautifulSoup
from typing import List, Dict, Any
import logging
import re

logger = logging.getLogger(__name__)

def parse_notices(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """
    BeautifulSoupオブジェクトからbutton.button_whiteまたはbutton.button_blueのテキスト内容と
    input[name='doc_id']のvalueを抽出し、リスト辞書形式で返す。

    Args:
        soup: BeautifulSoupオブジェクト

    Returns:
        List[Dict[str, Any]]: 抽出結果のリスト。各要素は分解された通知情報の辞書
    
    Raises:
        ValueError: HTMLパースエラーの場合
    """
    try:
        notices: List[Dict[str, Any]] = []

        # ボタン要素を取得
        buttons = soup.find_all('button', class_=['button_white', 'button_blue'])
        # 対応するinput[name='doc_id']を取得
        inputs = soup.find_all('input', attrs={'name': 'doc_id'})

        if len(buttons) != len(inputs):
            logger.warning(f"Button count ({len(buttons)}) doesn't match input count ({len(inputs)})")
        
        for btn, inp in zip(buttons, inputs):
            # ボタン内の文字列を結合
            label = ' '.join(btn.stripped_strings).replace('\u3000', ' ').strip()
            doc_id = inp.get('value', '')
            if label and doc_id:
                parsed_notice = _parse_label(label)
                parsed_notice['doc_id'] = doc_id
                notices.append(parsed_notice)

        logger.info(f"Parsed {len(notices)} notices from HTML")
        return notices
    
    except Exception as e:
        logger.error(f"Error parsing notices: {e}")
        return []


def _parse_label(label: str) -> Dict[str, str]:
    """
    ラベル文字列を分解して個別のフィールドを抽出する。
    
    Args:
        label: パースするラベル文字列
        
    Returns:
        Dict[str, str]: 分解された通知情報
    """
    # パターン例: （24年度第20回）権利行使の届出等 公告（07）第043号 令和７年４月２３日
    # パターン例: 25年度第03回債権消滅 公告（07）第072号 令和７年５月１日
    
    # 括弧付きパターンを先に試す
    pattern1 = r'（([^）]+)）([^公]*?)\s*公告（([^）]+)）第(\d+)号\s+(.+)'
    match = re.match(pattern1, label.strip())
    
    if match:
        notice_round = match.group(1)
        notice_type = match.group(2).strip()
        notice_number = f"公告（{match.group(3)}）第{match.group(4)}号"
        notice_date = match.group(5).strip()
        
        return {
            'notice_round': notice_round,
            'notice_type': notice_type,
            'notice_number': notice_number,
            'notice_date': notice_date
        }
    
    # 括弧なしパターンを試す
    pattern2 = r'([^公]+?)\s*公告（([^）]+)）第(\d+)号\s+(.+)'
    match = re.match(pattern2, label.strip())
    
    if match:
        # 年度回数と通知種類を分離
        round_and_type = match.group(1).strip()
        notice_number = f"公告（{match.group(2)}）第{match.group(3)}号"
        notice_date = match.group(4).strip()
        
        # 年度回数と通知種類を分離する正規表現
        round_type_pattern = r'(\d+年度第\d+回)(.+)'
        round_type_match = re.match(round_type_pattern, round_and_type)
        
        if round_type_match:
            notice_round = round_type_match.group(1)
            notice_type = round_type_match.group(2).strip()
        else:
            notice_round = round_and_type
            notice_type = ''
        
        return {
            'notice_round': notice_round,
            'notice_type': notice_type,
            'notice_number': notice_number,
            'notice_date': notice_date
        }
    
    # パースに失敗した場合は元のラベルを保持
    logger.warning(f"Failed to parse label: {label}")
    return {
        'notice_round': '',
        'notice_type': '',
        'notice_number': '',
        'notice_date': '',
        'label': label
    }