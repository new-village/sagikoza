from bs4 import BeautifulSoup
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def parse_accounts(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """
    Parse account information from HTML.
    
    Args:
        soup: BeautifulSoup object containing the HTML
        
    Returns:
        List of dictionaries containing account information
        
    Raises:
        ValueError: HTMLパースエラーの場合
    """
    try:
        containers = soup.select('div.container')

        def safe_get_text(element, *args, **kwargs):
            if element is None:
                return ''
            return element.get_text(*args, **kwargs)
        
        def split_account_type(account_type_text: str) -> tuple[str, str]:
            """
            Split combined account type data (e.g., "14000　　　　普通預金" -> ("14000", "普通預金"))
            
            Args:
                account_type_text: Raw account type text that may contain branch_code_alias
                
            Returns:
                Tuple of (branch_code_alias, account_type)
            """
            if not account_type_text:
                return '', ''
            
            text = account_type_text.strip()
            # Look for numeric code at the beginning followed by spaces and account type
            parts = text.split()
            if len(parts) >= 2 and parts[0].isdigit():
                branch_code_alias = parts[0]
                account_type = ''.join(parts[1:])
                return branch_code_alias, account_type
            else:
                return '', text
        
        def split_account_number(account_text: str) -> tuple[str, str]:
            """
            Split combined account number data (e.g., "7555041 755504" -> ("7555041", "755504"))
            
            Args:
                account_text: Raw account text that may contain account_alias
                
            Returns:
                Tuple of (account, account_alias)
            """
            if not account_text:
                return '', ''
            
            text = account_text.strip()
            # Split by space and check if we have two numeric parts
            parts = text.split()
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                return parts[0], parts[1]
            else:
                return text, ''
        
        def split_name_with_parentheses(name_text: str) -> tuple[str, str]:
            """
            Split name text with parentheses to extract katakana and alias.
            
            Args:
                name_text: Raw name text that may contain parentheses with katakana
                
            Returns:
                Tuple of (name, name_alias)
            """
            import re
            
            if not name_text:
                return '', ''
            
            text = name_text.strip().replace('\u3000', ' ')
            
            # Look for parentheses pattern
            match = re.search(r'（([^）]+)）', text)
            if match:
                parentheses_content = match.group(1).strip()
                # Check if content is katakana and more than one character
                if len(parentheses_content) > 1 and re.match(r'^[ァ-ヾ\s]+$', parentheses_content):
                    # Extract katakana as name, rest as name_alias
                    name = parentheses_content
                    name_alias = text.replace(match.group(0), '').strip()
                    return name, name_alias
            
            # If no valid parentheses content, return original as name
            return text, ''

        accounts = []
        for c in containers:
            account = {}
            account['role'] = safe_get_text(c.select_one('td.cat5'), strip=True).replace('■', '')
            account['bank_name'] = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(1) td.data'), strip=True)
            if c.select_one('table:nth-of-type(5)') is not None:
                # For JP Bank
                account['branch_name'] = safe_get_text(c.select_one('table:nth-of-type(4) tr:nth-of-type(2) td.data'), strip=True)
                account['branch_code'] = safe_get_text(c.select_one('table:nth-of-type(4) tr:nth-of-type(3) td.data'), strip=True)
                account['branch_code_alias'] = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(2) td.data'), strip=True)
                
                # Handle combined account_type with potential branch_code_alias
                raw_account_type = safe_get_text(c.select_one('table:nth-of-type(4) tr:nth-of-type(4) td.data'), strip=True)
                extracted_branch_code_alias, clean_account_type = split_account_type(raw_account_type)
                account['account_type'] = clean_account_type
                if extracted_branch_code_alias:
                    account['branch_code_alias'] = extracted_branch_code_alias
                
                # Handle combined account number with potential account_alias
                raw_account = safe_get_text(c.select_one('table:nth-of-type(4) tr:nth-of-type(5) td.data'), strip=True)
                clean_account, extracted_account_alias = split_account_number(raw_account)
                account['account'] = clean_account
                if extracted_account_alias:
                    account['account_alias'] = extracted_account_alias
                else:
                    account['account_alias'] = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(3) td.data'), strip=True)
                
                account['name'] = safe_get_text(c.select_one('table:nth-of-type(4) tr:nth-of-type(6) td.data'), strip=True).replace('\u3000', ' ')
                account['name_alias'] = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(4) td.data'), strip=True).replace('\u3000', ' ')
                
                # Check if name contains parentheses with katakana and split if needed
                raw_name = safe_get_text(c.select_one('table:nth-of-type(4) tr:nth-of-type(6) td.data'), strip=True)
                split_name, split_name_alias = split_name_with_parentheses(raw_name)
                if split_name_alias:  # If split was successful
                    account['name'] = split_name
                    account['name_alias'] = split_name_alias
                else:
                    account['name'] = raw_name.replace('\u3000', ' ')
                    account['name_alias'] = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(4) td.data'), strip=True).replace('\u3000', ' ')
                account['amount'] = safe_get_text(c.select_one('table:nth-of-type(5) tr:nth-of-type(1) td.data2'), strip=True).replace('★', '')
                account['effective_from'] = safe_get_text(c.select_one('table:nth-of-type(5) tr:nth-of-type(2) td:nth-of-type(3)'), strip=True)
                account['effective_to'] = safe_get_text(c.select_one('table:nth-of-type(5) tr:nth-of-type(2) td:nth-of-type(5)'), strip=True)
                account['effective_method'] = safe_get_text(c.select_one('table:nth-of-type(5) tr:nth-of-type(3) td.data'), strip=True)
                account['payment_period'] = safe_get_text(c.select_one('table:nth-of-type(5) tr:nth-of-type(4) td.data'), strip=True)
                account['suspend_date'] = safe_get_text(c.select_one('table:nth-of-type(5) tr:nth-of-type(5) td.data'), strip=True)
                account['notes'] = safe_get_text(c.select_one('table:nth-of-type(5) tr:nth-of-type(7) td.data'), strip=True)            
            elif c.select_one('table:nth-of-type(2) tr:nth-of-type(5)') is None:
                # For JP Bank Type 2
                if c.select_one('table:nth-of-type(2) tr:nth-of-type(4)'):
                    # Check if this is the special case with only 4 rows in table 2 (通帳記号/通帳番号)
                    table2_rows = c.select('table:nth-of-type(2) tr')
                    if len(table2_rows) == 4:
                        # Special case: ゆうちょ銀行 with 通帳記号/通帳番号
                        account['branch_code_alias'] = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(2) td.data'), strip=True)
                        account['account_alias'] = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(3) td.data'), strip=True)
                        
                        # Check if name contains parentheses with katakana and split if needed
                        raw_name = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(4) td.data'), strip=True)
                        split_name, split_name_alias = split_name_with_parentheses(raw_name)
                        if split_name_alias:  # If split was successful
                            account['name'] = split_name
                            account['name_alias'] = split_name_alias
                        else:
                            account['name'] = raw_name.replace('\u3000', ' ')
                            account['name_alias'] = raw_name.replace('\u3000', ' ')
                        account['amount'] = safe_get_text(c.select_one('table:nth-of-type(3) tr:nth-of-type(1) td.data2'), strip=True).replace('★', '')
                        account['suspend_date'] = safe_get_text(c.select_one('table:nth-of-type(3) tr:nth-of-type(2) td.data2'), strip=True)
                    else:
                        # Normal JP Bank Type 2 case
                        # Handle combined account_type with potential branch_code_alias
                        raw_account_type = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(2) td.data'), strip=True)
                        extracted_branch_code_alias, clean_account_type = split_account_type(raw_account_type)
                        
                        # If we extracted data from account_type field, use it; otherwise use existing logic
                        if extracted_branch_code_alias:
                            account['branch_code_alias'] = extracted_branch_code_alias
                            account['account_type'] = clean_account_type
                        else:
                            account['branch_code_alias'] = raw_account_type
                            account['account_type'] = ''
                        
                        # Handle combined account number with potential account_alias
                        raw_account = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(3) td.data'), strip=True)
                        clean_account, extracted_account_alias = split_account_number(raw_account)
                        account['account'] = clean_account
                        if extracted_account_alias:
                            account['account_alias'] = extracted_account_alias
                        else:
                            account['account_alias'] = raw_account
                        
                        # Check if name contains parentheses with katakana and split if needed
                        raw_name = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(4) td.data'), strip=True)
                        split_name, split_name_alias = split_name_with_parentheses(raw_name)
                        if split_name_alias:  # If split was successful
                            account['name'] = split_name
                            account['name_alias'] = split_name_alias
                        else:
                            account['name'] = raw_name.replace('\u3000', ' ')
                            account['name_alias'] = raw_name.replace('\u3000', ' ')
                        account['amount'] = safe_get_text(c.select_one('table:nth-of-type(3) tr:nth-of-type(1) td.data2'), strip=True).replace('★', '')
                        account['suspend_date'] = safe_get_text(c.select_one('table:nth-of-type(3) tr:nth-of-type(1) td.data2'), strip=True)
                else:
                    # Other case without 4th row
                    # Handle combined account_type with potential branch_code_alias
                    raw_account_type = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(2) td.data'), strip=True)
                    extracted_branch_code_alias, clean_account_type = split_account_type(raw_account_type)
                    
                    # If we extracted data from account_type field, use it; otherwise use existing logic
                    if extracted_branch_code_alias:
                        account['branch_code_alias'] = extracted_branch_code_alias
                        account['account_type'] = clean_account_type
                    else:
                        account['branch_code_alias'] = raw_account_type
                        account['account_type'] = ''
                    
                    # Handle combined account number with potential account_alias
                    raw_account = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(3) td.data'), strip=True)
                    clean_account, extracted_account_alias = split_account_number(raw_account)
                    account['account'] = clean_account
                    if extracted_account_alias:
                        account['account_alias'] = extracted_account_alias
                    else:
                        account['account_alias'] = raw_account
                    
                    account['amount'] = safe_get_text(c.select_one('table:nth-of-type(3) tr:nth-of-type(1) td.data2'), strip=True).replace('★', '')
                    account['suspend_date'] = safe_get_text(c.select_one('table:nth-of-type(3) tr:nth-of-type(1) td.data2'), strip=True)
            else:
                # For other banks
                account['branch_name'] = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(2) td.data'), strip=True)
                account['branch_code'] = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(3) td.data'), strip=True)
                
                # Handle combined account_type with potential branch_code_alias
                raw_account_type = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(4) td.data'), strip=True)
                extracted_branch_code_alias, clean_account_type = split_account_type(raw_account_type)
                account['account_type'] = clean_account_type
                if extracted_branch_code_alias:
                    account['branch_code_alias'] = extracted_branch_code_alias
                
                # Handle combined account number with potential account_alias
                raw_account = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(5) td.data'), strip=True)
                clean_account, extracted_account_alias = split_account_number(raw_account)
                account['account'] = clean_account
                if extracted_account_alias:
                    account['account_alias'] = extracted_account_alias
                
                # Check if name contains parentheses with katakana and split if needed
                raw_name = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(6) td.data'), strip=True)
                split_name, split_name_alias = split_name_with_parentheses(raw_name)
                if split_name_alias:  # If split was successful
                    account['name'] = split_name
                    account['name_alias'] = split_name_alias
                else:
                    account['name'] = raw_name.replace('\u3000', ' ')
                account['amount'] = safe_get_text(c.select_one('table:nth-of-type(3) tr:nth-of-type(1) td.data2'), strip=True).replace('★', '')
                account['effective_from'] = safe_get_text(c.select_one('table:nth-of-type(3) tr:nth-of-type(2) td:nth-of-type(3)'), strip=True)
                account['effective_to'] = safe_get_text(c.select_one('table:nth-of-type(3) tr:nth-of-type(2) td:nth-of-type(5)'), strip=True)
                account['effective_method'] = safe_get_text(c.select_one('table:nth-of-type(3) tr:nth-of-type(3) td.data'), strip=True)
                account['payment_period'] = safe_get_text(c.select_one('table:nth-of-type(3) tr:nth-of-type(4) td.data'), strip=True)
                account['suspend_date'] = safe_get_text(c.select_one('table:nth-of-type(3) tr:nth-of-type(5) td.data'), strip=True)
                account['notes'] = safe_get_text(c.select_one('table:nth-of-type(3) tr:nth-of-type(7) td.data'), strip=True)
            # Only add account if it has meaningful data
            if any(account.values()):
                accounts.append(account)

        logger.debug(f"Parsed {len(accounts)} accounts from HTML")
        return accounts
    
    except Exception as e:
        logger.error(f"Error parsing accounts: {e}")
        return []
