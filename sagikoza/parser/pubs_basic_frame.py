from bs4 import BeautifulSoup
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def parse_subject(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """
    Parse subject information from HTML.
    
    Args:
        soup: BeautifulSoup object containing the HTML
        
    Returns:
        List of dictionaries containing subject information
        
    Raises:
        ValueError: HTMLパースエラーの場合
    """
    try:
        forms = soup.find_all('form', attrs={'name': 'list_form'})
        form_vals = [form.get('action').replace('./', '') for form in forms if form.has_attr('action')]

        inputs = soup.find_all('input', attrs={'name': 'r_no'})
        input_vals = [input.get('value').strip() for input in inputs if input.has_attr('value')]

        if len(form_vals) != len(input_vals):
            logger.warning(f"Form count ({len(form_vals)}) doesn't match input count ({len(input_vals)})")

        # Ensure we have unique pairs of form and input values
        unique_subjects = set((form, input) for form, input in zip(form_vals, input_vals) if form and input)
        subjects = [{'form': form, 'no': input} for form, input in unique_subjects]
        subjects.sort(key=lambda x: x['no'])

        logger.info(f"Parsed {len(subjects)} subjects from HTML")
        return subjects
    
    except Exception as e:
        logger.error(f"Error parsing subjects: {e}")
        return []
