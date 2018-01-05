# -*- coding: utf-8 -*-
import click
from . import load_file


@click.command()
@click.argument('file_path', type=click.Path(exists=True))
def main(file_path):
    emails = load_file(file_path)
    click.echo(emails)
    click.echo(len(emails))
