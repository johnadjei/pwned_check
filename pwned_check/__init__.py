# -*- coding: utf-8 -*-
import re
import time
import click
import requests
import csv
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


EMAIL_REGEX_1 = r'[^@]+@[^@]+\.[^@]+'
EMAIL_REGEX_2 = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
PWNED_USER_AGENT = 'pwned_checker 0.1'
PWNED_API_VERSION = 2
PWNED_API_URI_FMT_BREACHED = 'https://haveibeenpwned.com/api/v{api_version}/breachedaccount/{email}'
PWNED_API_URI_FMT_PASTE = 'https://haveibeenpwned.com/api/v{api_version}/pasteaccount/{email}'


def retryable_session(
    retries=2,
    backoff_factor=0.66667,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    return session


def parse_email(email_address) -> str:
    compiled_regex = re.compile(EMAIL_REGEX_2)
    if not compiled_regex.match(email_address):
        return ''

    return email_address.strip()


def load_file(spreadsheet_file) -> list:
    with open(spreadsheet_file, 'r') as input_file:
        emails = input_file.readlines()

    return list(filter(None, list(map(lambda e: parse_email(e), emails))))


def serialize_response(email: str, resp_type: str, resp_json: {}) -> dict:
    if resp_type == 'breaches':
        # fieldnames = ['email', 'breach_date', 'title', 'data_classes']
        return {
            'email': email,
            'breach_date': resp_json['BreachDate'],
            'title': resp_json['Title'],
            'data_classes': '|'.join(resp_json['DataClasses']),
        }
    elif resp_type == 'pastes':
        # fieldnames = ['email', 'date', 'source', 'title', 'email_count']
        return {
            'email': email,
            'date': resp_json['Date'][:10],
            'source': resp_json['Source'],
            'title': resp_json['Title'] if 'Title' in resp_json else '',
            'email_count': int(resp_json['EmailCount']) if 'EmailCount' in resp_json else 0,
        }
    else:
        return {}


def make_requests(api: str, emails: list, params=None) -> tuple:
    request_session = retryable_session()
    request_headers = {'user-agent': PWNED_USER_AGENT}
    passed_emails = []
    failed_emails = []

    for email in emails:
        try:
            url = PWNED_API_URI_FMT_BREACHED.format(api_version=PWNED_API_VERSION,
                                                    email=email)
            if api == 'pastes':
                url = PWNED_API_URI_FMT_PASTE.format(api_version=PWNED_API_VERSION,
                                                     email=email)
            click.echo('{email}: Getting {api} data...'.format(email=email, api=api))
            resp = request_session.get(url, headers=request_headers, params=params)
        except Exception as exc:
            msg = '{email}: Failed with {status}, {reason}'.format(email=email,
                                                                   status=resp.status_code,
                                                                   reason=resp.reason)
            click.echo(msg)
            failed_emails.append({'email': email, 'status': resp.status_code, 'reason': resp.reason})
        else:
            for rec in resp.json():
                resp_serialized = serialize_response(email, api, rec)
                passed_emails.append(resp_serialized)
        finally:
            time.sleep(2)
    return passed_emails, failed_emails


def save_response_emails(emails: [], output_file: str, field_names: []) -> bool:
    if emails:
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()
            writer.writerows(emails)
        click.echo('CSV output written to "{outfile}"'.format(outfile=output_file))
        return True
    return False
