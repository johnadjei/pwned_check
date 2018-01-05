# -*- coding: utf-8 -*-
import time
import click
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from . import load_file
import csv


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


PWNED_USER_AGENT = 'pwned_checker 0.1'
PWNED_API_VERSION = 2
PWNED_API_URI_FMT_BREACHED = 'https://haveibeenpwned.com/api/v{api_version}/breachedaccount/{email}'
PWNED_API_URI_FMT_PASTE = 'https://haveibeenpwned.com/api/v{api_version}/pasteaccount/{email}'


@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path(exists=False))
def main(input_file, output_file):
    emails = load_file(input_file)
    request_headers = {'user-agent': PWNED_USER_AGENT}
    request_payload = {'includeUnverified': True}
    request_session = retryable_session()
    fieldnames = ['email', 'breach_date', 'title', 'data_classes']
    passed_emails = []
    failed_emails = []

    for email in emails:
        url = PWNED_API_URI_FMT_BREACHED.format(api_version=PWNED_API_VERSION,
                                                email=email)

        try:
            click.echo('{email}: Getting breach data...'.format(email=email))
            resp = request_session.get(url, headers=request_headers, params=request_payload)
        except Exception as x:
            msg = '{email}: Failed with {status}, {reason}'.format(email=email,
                                                                   status=resp.status_code,
                                                                   reason=resp.reason)
            click.echo(msg)
            failed_emails.append({'email': email, 'status': resp.status_code, 'reason': resp.reason})
        else:
            for rec in resp.json():
                passed_emails.append({
                    'email': email,
                    'breach_date': rec['BreachDate'],
                    'title': rec['Title'],
                    'data_classes': '|'.join(rec['DataClasses']),
                })
        finally:
            time.sleep(2)

    if passed_emails:
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(passed_emails)
        click.echo('CSV output written to "{outfile}"'.format(outfile=output_file))
