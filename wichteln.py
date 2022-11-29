import csv
import getpass
import json
import os
import random
import smtplib
import time
from email.message import EmailMessage
import typing

import click
import cpmpy as cp
import matplotlib.pyplot as plt
import networkx as nx
import tabulate


def read_participants(path: str) -> typing.Dict[str, dict]:
    participants = {}
    with open(path, 'r') as file:
        reader = csv.reader(file, delimiter=',', )
        for i, row in enumerate(reader):
            participants[row[0]] = dict(
                id=i + 1,
                name=row[0],
                constraints=row[1],
                email=row[2]
            )
            if len(row) == 4:
                participants[row[0]]['wichtel'] = row[3]
        return participants

def check_assignment(assignments: dict):
    for name, p in assignments.items():
        if 'wichtel' not in p.keys():
            raise ValueError('No assignments found.')
        constraints = set(p['constraints'].split(';'))
        if p['wichtel'] in constraints:
            raise ValueError(f'Assignment of {name} to {p["wichtel"]} violates constraints.')


def show_table(assignments: dict, show_names: bool):
    if not show_names:
        assignments = dict((k, {**v, 'wichtel': '*****'}) for k, v in assignments.items())
    headers = list(assignments[list(assignments.keys())[0]].keys())
    table = tabulate.tabulate(
        tabular_data=[[e for e in row.values()] for row in assignments.values()],
        headers=headers
    )
    print(table)

def build_message(participant: dict, mail_config: dict):
        msg = EmailMessage()
        template = open(mail_config['body_template']).read()
        msg.set_content(template % (participant['name'], participant['wichtel']))
        msg['Subject'] = mail_config['subject']
        msg['From'] = mail_config['sender']
        msg['To'] = participant['email']
        return msg

@click.group()
def cli():
    pass

@click.command()
@click.argument('participants', type=str)
@click.option('--output-file', type=str)
def generate(participants, output_file):
    contacts = read_participants(participants)
    model = cp.Model()
    names = sorted(list(contacts.keys()))
    assignments = cp.intvar(0, len(contacts) - 1, shape=(len(contacts),))
    model += cp.Circuit(assignments)
    for name, person in contacts.items():
        i = names.index(name)
        for constraint in [c for c in person['constraints'].split(';') if c != '']:
            j = names.index(constraint)
            model += assignments[i] != j

    solutions = []
    n = model.solveAll(display=lambda: solutions.append(assignments.value()), solution_limit=1000)
    print(f'Found {n} solutions.')
    print(f'Writing to {output_file}.')
    sampled_solution = random.choice(solutions)
    with open(output_file, 'w') as file:
        writer = csv.writer(file, delimiter=',')
        for name, person in  contacts.items():
            i = names.index(name)
            wichtel_index = sampled_solution[i]
            writer.writerow([name, person['constraints'], person['email'], names[wichtel_index]])


@click.command()
@click.argument('assignments', type=click.Path(exists=True))
@click.option('--show-names', is_flag=True, show_default=False, default=False)
def show(assignments: str, show_names: bool):
    assignments = read_participants(assignments)
    show_table(assignments, show_names)

@click.command()
@click.argument('assignments', type=click.Path(exists=True))
@click.option('--show-names', is_flag=True, show_default=False, default=False)
def visualize(assignments: str, show_names: bool):
    G = nx.DiGraph()
    assignments = read_participants(assignments)
    for name, p in assignments.items():
        G.add_edge(name, p['wichtel'])
    nx.draw(G, with_labels=show_names)
    plt.show()


def send_emails(assignments: dict, password: str, mail_config: dict):
    with smtplib.SMTP(mail_config['host'], mail_config['port']) as server:
        server.starttls()
        server.login(mail_config['sender'], password)
        print('Login successful.')
        errors = {}
        names = sorted(list(assignments.keys()))
        for name in names:
            i = names.index(name)
            p = assignments[name]
            message = build_message(participant=p, mail_config=mail_config)
            try:
                server.send_message(message)
                status = 'Ok'
            except smtplib.SMTPException as e:
                status = 'Error ({})'.format(e)
                errors[name] = e
            print(f'[{i + 1}/{len(names)}] Sending email to {name} ({p["email"]}): {status}')
    return errors

@click.command()
@click.argument('assignments', type=click.Path(exists=True))
@click.option('--mail-config', type=str)
@click.option('--participants', type=str, default='')
def send(assignments: str, mail_config: str, participants: str):
    assignments = read_participants(assignments)
    try:
        check_assignment(assignments)
        with open(mail_config, 'r') as file:
            mail_config = json.load(file)
    except ValueError | Exception as e:
        print(e)
        return

    print("Sending emails out to participants:\n")
    if participants != '':
        participants = participants.split(',')
        assignments = dict((k, v) for k, v in assignments.items() if k in participants)
    show_table(assignments, show_names=False)
    password = getpass.getpass("\nType your password and press enter: ")
    try_send = True
    try:
        while try_send:
            errors = send_emails(assignments, password, mail_config)
            if len(errors) > 0:
                print('\nErrors occured while sending emails.')
                try_send = click.confirm('Do you want to retry failed attempts?')
                assignments = dict((k, v) for k, v in assignments.items() if k in errors.keys())
            else:
                try_send = False
    except smtplib.SMTPException as e:
        print(f'Error: {e}')
        return

if __name__ == '__main__':
    cli.add_command(show)
    cli.add_command(send)
    cli.add_command(generate)
    cli.add_command(visualize)
    cli()