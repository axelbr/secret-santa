import click
import networkx as nx
from matplotlib import pyplot as plt

from wichteln.utils import read_participants, decrypt_assignments


@click.command(help='Visualize the assignments as a graph.')
@click.argument('assignments', type=click.Path(exists=True))
@click.option('--show-names', is_flag=True, show_default=False, default=False,
              help='Show the names of the participants.')
@click.option('--password', type=str, default=None, help='Password to decrypt the assignments file.')
def visualize(assignments: str, show_names: bool, password: str):
    G = nx.DiGraph()
    assignments = read_participants(assignments)
    if password:
        assignments = decrypt_assignments(assignments, password) or dict()
    for name, p in assignments.items():
        G.add_edge(name, p['wichtel'])
    nx.draw(G, with_labels=show_names)
    plt.show()


def make():
    return visualize
