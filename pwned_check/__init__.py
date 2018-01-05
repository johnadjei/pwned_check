import re


EMAIL_REGEX_1 = r'[^@]+@[^@]+\.[^@]+'
EMAIL_REGEX_2 = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

def parse_email(email_address) -> str:
    compiled_regex = re.compile(EMAIL_REGEX_2)
    if not compiled_regex.match(email_address):
        return ''

    return email_address.strip()


def load_file(spreadsheet_file) -> list:
    with open(spreadsheet_file, 'r') as input_file:
        emails = input_file.readlines()

    return list(filter(None, list(map(lambda e: parse_email(e), emails))))
