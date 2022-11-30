import base64
import csv
import typing

import tabulate
from cryptography.fernet import Fernet
from hashlib import scrypt
from os import urandom
from base64 import urlsafe_b64encode


def print_table(assignments: dict, show_names: bool):
    if not show_names:
        assignments = dict((k, {**v, 'wichtel': '*****'}) for k, v in assignments.items())
    headers = list(list(assignments.values())[0].keys())
    table = tabulate.tabulate(
        tabular_data=[[e for e in row.values()] for row in assignments.values()],
        headers=headers
    )
    print(table)

def read_participants(path: str) -> typing.Dict[str, dict]:
    participants = {}
    with open(path, 'r') as file:
        reader = csv.reader(file, delimiter=',', )
        for i, row in enumerate(reader):
            participants[row[0]] = dict(
                id=i + 1,
                name=row[0],
                constraints=row[1],
                email=row[2],
            )
            if len(row) == 5:
                participants[row[0]]['wichtel'] = row[3]
                participants[row[0]]['delivered'] = row[4]
        return participants

def write_assignments_to_file(assignments: dict[str, dict], path: str):
    with open(path, 'w') as file:
        writer = csv.writer(file, delimiter=',')
        names = sorted(list(assignments.keys()))
        for name in names:
            person = assignments[name]
            writer.writerow([name, person['constraints'], person['email'], person['wichtel'], person['delivered']])

def check_assignment(assignments: dict):
    for name, p in assignments.items():
        if 'wichtel' not in p.keys():
            raise ValueError('No assignments found.')
        constraints = set(p['constraints'].split(';'))
        if p['wichtel'] in constraints:
            raise ValueError(f'Assignment of {name} to {p["wichtel"]} violates constraints.')

def decrypt_assignments(assignments: dict, password: str) -> dict:
    assignments = assignments.copy()
    for k, v in assignments.items():
        v['wichtel'] = decrypt(v['wichtel'], password)
    return assignments

def encrypt(string, password):
    """
    Encrypts a message
    """
    return string
def decrypt(string, password):
    """
    Encrypts a message
    """
    return string
