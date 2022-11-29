import csv
import getpass
import random
import smtplib
import ssl
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
                firstname=row[0],
                constraints=row[1],
                email=row[2]
            )
            if len(row) == 4:
                participants[row[0]]['wichtel'] = row[3]
        return participants


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
    for i, name in enumerate(names):
        contacts[name]['wichtel'] = names[sampled_solution[i]]

    assignments = {}
    with open(output_file, 'w') as file:
        writer = csv.writer(file, delimiter=',')
        for name, person in contacts.items():
            writer.writerow([name, person['constraints'], person['email'], person['wichtel']])


@click.command()
@click.argument('assignments', type=click.Path(exists=True))
@click.option('--show-names', is_flag=True, show_default=False, default=False)
def show(assignments: str, show_names: bool):
    assignments = read_participants(assignments)
    for name, p in assignments.items():
        assert 'wichtel' in p, 'No assignments found.'
    if not show_names:
        assignments = dict((k, {**v, 'wichtel': '*****'}) for k, v in assignments.items())
    print(tabulate.tabulate([[e for e in row.values()] for row in assignments.values()],
                            headers=assignments[list(assignments.keys())[0]].keys()))


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


@click.command()
@click.argument('assignments', type=click.Path(exists=True))
@click.option('--email', type=str)
@click.option('--port', type=int, default=1025)
@click.option('--host', type=str, default='localhost')
def send(assignments: str, email: str, port, host):
    assignments = read_participants(assignments)
    for name, p in assignments.items():
        assert 'wichtel' in p, 'No assignments found.'
    show_assignments = assignments.copy()
    show_assignments = dict((k, {**v, 'wichtel': '*****'}) for k, v in show_assignments.items())
    print(tabulate.tabulate([[e for e in row.values()] for row in show_assignments.values()],
                            headers=assignments[list(assignments.keys())[0]].keys()))
    print()
    password = getpass.getpass("Sending emails out to all participants.\nType your password and press enter: ")
    template = open('data/message_template.txt', 'r').read()
    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(email, password)
        print('Login successful.')
        with click.progressbar(label='Sending mails...', iterable=assignments.items()) as bar:
            for name, p in bar:
                msg = template % (name, p['wichtel'])
                server.sendmail(
                    from_addr=email,
                    to_addrs=p['email'],
                    msg=msg
                )
        server.quit()


if __name__ == '__main__':
    cli.add_command(show)
    cli.add_command(send)
    cli.add_command(generate)
    cli.add_command(visualize)
    cli()