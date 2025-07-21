from bs4 import BeautifulSoup


def parse_submit(soup: BeautifulSoup) -> list:
    """
    Extracts publication details from the BeautifulSoup object.

    Args:
        soup: BeautifulSoup object containing the HTML of the publication page.

    Returns:
        A list of dictionaries, each containing details of a publication.
    """
    submit = []
    links = soup.select('tr > td.\\36 > a')
    for link in links:
        params = {}
        href = link.get('href').replace('./pubs_basic_frame.php?', '')
        for param in href.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                params[key] = value
        params['params'] = href
        submit.append(params)

    return submit

