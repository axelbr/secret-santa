import email.message
import getpass
import smtplib
from email.message import EmailMessage
import yaml
import click

from wichteln.utils import read_participants, check_assignment, print_table, write_assignments_to_file, \
    decrypt_assignments


def compose_emails(participants: dict, mail_config: dict):
    names = sorted(list(participants.keys()))
    emails = {}
    for name in names:
        i = names.index(name)
        p = participants[name]
        msg = EmailMessage()
        template = mail_config['body_template']
        msg.set_content(template % (p['name'], p['wichtel']))
        msg['Subject'] = mail_config['subject']
        msg['From'] = mail_config['sender']
        msg['To'] = p['email']
        emails[name] = msg
    return emails

def send_email(email: email.message.Message, server: smtplib.SMTP):
    try:
        server.send_message(email)
        return True, 'Ok'
    except smtplib.SMTPException as e:
        status = 'Error ({})'.format(e)
        return False, status


def send_emails(emails: dict[str, email.message.EmailMessage], password: str, mail_config: dict, dry_run=False):
    sender, host, port = mail_config['sender'], mail_config['host'], mail_config['port']
    try:
        server = smtplib.SMTP(host, int(port))
        if mail_config['use_tls']:
            server.starttls()
        server.login(sender, password)
    except smtplib.SMTPException as e:
        print(f'Error: {e}')
        return []


    completed = list()
    names = sorted(list(emails.keys()))
    for i, name in enumerate(names):
        if dry_run:
            is_ok, status = True, 'Dry run.'
        else:
            is_ok, status = send_email(emails[name], server)

        if is_ok:
            completed.append(name)
        print(f'Sending mail to {name} ({emails[name]["To"]}): {status}')
    return completed


def display_emails(messages: dict[str, EmailMessage]):
    for name, message in messages.items():
        print(message.as_string())
        print('----------------------------------')

@click.command()
@click.argument('assignments', type=click.Path(exists=True))
@click.option('--mail-config', type=str, required=True, help='Path to mail config file')
@click.option('--participants', type=str, default='', help='Specify participants to send mails to.')
@click.option('--dry-run', type=bool, is_flag=True, help='Do not send emails')
@click.option('--password', type=str, default=None, help='Password to decrypt the assignments file')
def send(assignments: str, mail_config: str, participants: str, dry_run: bool, password):
    assignments_file = assignments
    assignments = read_participants(assignments)
    if password:
        assignments = decrypt_assignments(assignments, password) or dict()
    try:
        check_assignment(assignments)
        with open(mail_config, 'r') as file:
            mail_config = yaml.load(file, yaml.SafeLoader)
    except ValueError | Exception as e:
        print(e)
        return

    if participants != '':
        participants = participants.split(',')
        assignments_to_send = dict((k, v) for k, v in assignments.items() if k in participants)
    else:
        assignments_to_send = dict((k, v) for k, v in assignments.items() if v['delivered'] == 'False')

    if len(assignments_to_send) == 0:
        print('Nothing to do. Bye.')
        return
    print("Sending emails out to participants:\n")
    print_table(assignments_to_send, show_names=False)
    emails = compose_emails(assignments_to_send, mail_config=mail_config)


    password = getpass.getpass("\nType your password and press enter: ")
    try_send = True
    while try_send:
        if dry_run:
            display_emails(emails)
            completed = list(assignments_to_send.keys())
        else:
            completed = send_emails(emails, password=password, mail_config=mail_config, dry_run=dry_run)
        for name in completed:
            assignments[name]['delivered'] = True
            emails.pop(name)
        if len(emails) > 0:
            print('\nErrors occured while sending emails.')
            try_send = click.confirm('Do you want to retry failed attempts?')
        else:
            try_send = False
    write_assignments_to_file(assignments, path=assignments_file)


def make():
    return send
