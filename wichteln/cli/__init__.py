import click

from wichteln.cli import generate, send, show, visualize


@click.group()
def wichteln():
    pass


wichteln.add_command(generate.make())
wichteln.add_command(send.make())
wichteln.add_command(show.make())
wichteln.add_command(visualize.make())
