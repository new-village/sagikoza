from bs4 import BeautifulSoup

def parse_accounts(soup: BeautifulSoup) -> list:
    tables = soup.select('div.container')

    accounts = []
    for table in tables:
        account = {}
        account['role'] = table.select_one('td.cat5').get_text(strip=True).replace('■', '')
        account['bank_name'] = table.select_one('table:nth-of-type(2) tr:nth-of-type(1) td.data').get_text(strip=True)
        account['branch_name'] = table.select_one('table:nth-of-type(2) tr:nth-of-type(2) td.data').get_text(strip=True)
        account['branch_code'] = table.select_one('table:nth-of-type(2) tr:nth-of-type(3) td.data').get_text(strip=True)
        account['account_type'] = table.select_one('table:nth-of-type(2) tr:nth-of-type(4) td.data').get_text(strip=True)
        account['account'] = table.select_one('table:nth-of-type(2) tr:nth-of-type(5) td.data').get_text(strip=True)
        account['name'] = table.select_one('table:nth-of-type(2) tr:nth-of-type(6) td.data').get_text(strip=True).replace('\u3000', ' ')
        account['amount'] = table.select_one('table:nth-of-type(3) tr:nth-of-type(1) td.data2').get_text(strip=True).replace('★', '')
        account['effective_from'] = table.select_one('table:nth-of-type(3) tr:nth-of-type(2) td:nth-of-type(3)').get_text(strip=True)
        account['effective_to'] = table.select_one('table:nth-of-type(3) tr:nth-of-type(2) td:nth-of-type(5)').get_text(strip=True)
        account['effective_method'] = table.select_one('table:nth-of-type(3) tr:nth-of-type(3) td.data').get_text(strip=True)
        account['payment_period'] = table.select_one('table:nth-of-type(3) tr:nth-of-type(4) td.data').get_text(strip=True)
        account['suspend_date'] = table.select_one('table:nth-of-type(3) tr:nth-of-type(5) td.data').get_text(strip=True)
        account['notes'] = table.select_one('table:nth-of-type(3) tr:nth-of-type(7) td.data').get_text(strip=True)
        accounts.append(account)

    return accounts
