import click

from wichteln.utils import read_participants, print_table, decrypt_assignments


@click.command()
@click.argument('assignments', type=click.Path(exists=True))
@click.option('--show-names', is_flag=True, show_default=False, default=False,
              help='Show the names of the participants.')
@click.option('--password', type=str, default=None, help='Password to decrypt the assignments file.')
def show(assignments: str, show_names: bool, password):
    assignments = read_participants(assignments)
    if password:
        assignments = decrypt_assignments(assignments, password)
    if assignments:
        print_table(assignments, show_names)


def make():
    return show
