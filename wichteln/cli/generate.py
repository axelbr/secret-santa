import csv
import random
from cryptography.fernet import Fernet

import click as click
import cpmpy as cp

from wichteln.utils import read_participants, write_assignments_to_file, encrypt


def make() -> click.Command:
    return generate


@click.command()
@click.argument('participants', type=str)
@click.option('--output-file', type=str)
@click.option('--password', type=str, default=None)
def generate(participants, output_file, password):
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
    for name, person in contacts.items():
        i = names.index(name)
        wichtel_index = sampled_solution[i]
        wichtel = names[wichtel_index]
        if password:
            wichtel = encrypt(wichtel, password)
        person['wichtel'] = wichtel
        person['delivered'] = False
    write_assignments_to_file(contacts, path=output_file)




