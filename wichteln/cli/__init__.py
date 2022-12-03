import click

from wichteln.cli import generate, send, show, visualize


@click.group(
    name='wichteln',
    help='A simple CLI tool to generate and send secret santa assignments.',

)
def wichteln():
    pass


wichteln.add_command(generate.make())
wichteln.add_command(send.make())
wichteln.add_command(show.make())
wichteln.add_command(visualize.make())
