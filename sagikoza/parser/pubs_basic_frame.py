from bs4 import BeautifulSoup

def parse_subject(soup: BeautifulSoup) -> list:
    forms = soup.find_all('form', attrs={'name': 'list_form'})
    form_vals = [form.get('action').replace('./', '') for form in forms if form.has_attr('action')]

    inputs = soup.find_all('input', attrs={'name': 'r_no'})
    input_vals = [input.get('value').strip() for input in inputs if input.has_attr('value')]

    # Ensure we have unique pairs of form and input values
    unique_subjects = set((form, input) for form, input in zip(form_vals, input_vals))
    subjects = [{'form': form, 'no': input} for form, input in unique_subjects]
    subjects.sort(key=lambda x: x['no'])

    return subjects
