from typing import Any, Dict, List
import unicodedata
import re

def normalize_accounts(account: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Normalize account data by generating unique identifiers.
    
    Args:
        accounts (Dict[str, Any]): Dictionary of account data.
        
    Returns:
        List[Dict[str, Any]]: List of accounts with unique identifiers.
    """
    if 'error' in account:
        return [account]  # Return the account with error as-is

    # Generate a unique identifier for the account
    for field in ['name', 'name_alias']:
        if field in account and isinstance(account[field], str):
            # 濁点と半濁点を合成可能な濁点と半濁点に標準化
            account[field] = account[field].replace('\u309B', '\u3099').replace('\u309C', '\u309A')
            # 長音を標準化
            account[field] = re.sub(r'[-˗ᅳ᭸‐‑‒–—―⁃⁻−▬─━➖ーㅡ﹘﹣－ｰ𐄐𐆑]', 'ー', account[field])
            # 括弧以外の文字列を標準化
            account[field] = unicodedata.normalize('NFKC', account[field]).replace('(', '（').replace(')', '）')
    
    # nameフィールドが「半角英数スペース (全角カナ半角スペース３文字以上)」の場合、分割する
    if 'name' in account and isinstance(account['name'], str):
        m = re.match(r'^([A-Za-z0-9 ]+)\s*\（([\u30A0-\u30FF\s]{3,})\）$', account['name'])
        if m:
            account['name'] = m.group(2).strip()
            account['name_alias'] = m.group(1).strip()
    
    # 日付け関連のフィールドをdate型に変換
    for date_field in ['notice_date', 'suspend_date', 'delete_date']:
        if date_field in account and isinstance(account[date_field], str):
            # 例: '2024年6月5日' -> '2024-06-05'
            try:
                m = re.match(r'(\d{4})年(\d{1,2})月(\d{1,2})日', account[date_field])
                if m:
                    year, month, day = m.groups()
                    account[date_field] = f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
            except Exception:
                pass
    
    #9 異常値の修正（2505-0543-0040 対応）
    # account_typeに5桁の数字が含まれている場合、抽出してbranch_code_jpbに入れる
    if 'account_type' in account and isinstance(account['account_type'], str):
        parts = account['account_type'].split()
        if len(parts) == 2:
            account['branch_code_jpb'] = parts[0].strip()
            account['account_type'] = parts[1].strip()
    # accountフィールドを分割してaccount_jpbとaccountに格納
    if 'account' in account and isinstance(account['account'], str):
        parts = account['account'].split()
        if len(parts) == 2:
            account['account_jpb'] = parts[0].strip().zfill(8)
            account['account'] = parts[1].strip().zfill(7)

    #7 ゆうちょ銀行レコードの支店名と口座番号の登録
    if ('branch_code' not in account or not account['branch_code']) and 'branch_code_jpb' in account and account['branch_code_jpb']:
        bcj = account['branch_code_jpb']
        if len(bcj) >= 3:
            if bcj[0] == '1':
                branch_code = f"{bcj[1:3]}8"
                account['account_type'] = '普通預金'
            elif bcj[0] == '0':
                branch_code = f"{bcj[1:3]}9"
                account['account_type'] = '振替口座'
            else:
                branch_code = ''
            if branch_code:
                account['branch_code'] = branch_code.zfill(3)
                # 漢数字変換
                kanji_digits = {'0': '〇', '1': '一', '2': '二', '3': '三', '4': '四', '5': '五', '6': '六', '7': '七', '8': '八', '9': '九'}
                account['branch_name'] = ''.join(kanji_digits.get(d, d) for d in account['branch_code'])

    if ('account' not in account or not account['account']) and 'account_jpb' in account and account['account_jpb']:
        acc_jpb = account['account_jpb'][:7]
        account['account'] = acc_jpb.zfill(7)

    return [account]