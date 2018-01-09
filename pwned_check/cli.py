# -*- coding: utf-8 -*-
import click
from . import load_file, make_requests, save_response_emails


@click.group()
@click.pass_context
def main(context):
    context.obj = {}


@main.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path(exists=False))
@click.pass_context
def breaches(context, input_file, output_file):
    emails = load_file(input_file)
    request_payload = {'includeUnverified': True}
    fieldnames = ['email', 'breach_date', 'title', 'data_classes']
    passed_emails, failed_emails = make_requests('breaches', emails, params=request_payload)

    if passed_emails:
        save_response_emails(passed_emails, output_file, field_names=fieldnames)


@main.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path(exists=False))
@click.pass_context
def pastes(context, input_file, output_file):
    emails = load_file(input_file)
    fieldnames = ['email', 'date', 'source', 'title', 'email_count']
    passed_emails, failed_emails = make_requests('pastes', emails)

    if passed_emails:
        save_response_emails(passed_emails, output_file, field_names=fieldnames)


@main.command()
def passwords():
    click.echo('Unimplemented')
