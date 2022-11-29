# Wichtel App
A CLI app to generate assignments for the secret santa game.

## Installation
```bash
git clone git@github.com:axelbr/secret-santa.git
cd secret-santa
python3 -m venv venv && source venv/bin/activate # optional
pip install -r requirements.txt # install requirements
```

## Usage
Generating Assignments:

`python main.py generate --output-file=<path> <path/to/contacts.csv>`

After generating assignments, you can display them on the command line (the assigned names won't be shown):

`python main.py show <assignments.csv>`

You can also display a graph that shows who is the santa of which person. If you do not want to display the assigned names,
you can remove the `--show-names` flag.

`python main.py visualize --show-names <assignments.csv>`

To send a mail with the assigned name to each of the participants, you can call the `send` command:

`python main.py send --email <your-email> --host <hostname> --port <port> <assignments.csv>`