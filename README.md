# Wichtel App
A CLI app to generate assignments for the secret santa (a.k.a *wichteln* in Austria) game.

## Installation
```bash
pip install git+https://github.com/axelbr/secret-santa.git
```

## Usage


### Generating Assignments 
To generate assignments for a group of people, create a CSV file with three columns (separated by a comma):
1. Column: The identifying name of a person
2. A list of names which should not be assigned to the person in the first column (separated by a semicolon)
3. The email address of the person.

For example, the following table contains four participants:

| Name  | Constraint | Email              |
|-------|------------|--------------------|
| Axel  | Bob;Alice  | axel@hostname.com  |
| Bob   |            | bob@hostname.com   |
| Alice | Bob        | alice@hostname.com |
| Tom   | Alice      | tom@hostname.com   |

The corresponding CSV file would look like this:
```csv
Axel,Bob;Alice,axel@hostname.com
Bob,,bob@hostname.com
Alice,Bob,alice@hostname.com
Tom,Alice,tom@hostname.com
```

This file can be used to generate assignments with the following command:
```bash
wichteln generate --output-file=<path> <path/to/contacts.csv>
```

The generated assignments are written to the specified output file. The file looks similar to the 
participants file, but contains additional information: The name of the person to whom the person was
assigned and the delivery status (i.e. whether the assignment was sent to the person via email).

For instance:

| Name  | Constraint | Email              |Wichtel| Delivered |
|-------|------------|--------------------|---|-----------|
| Axel  | Bob;Alice  | axel@hostname.com  |Tom| False     |
| Bob   |            | bob@hostname.com   |Alice| False     |
| Alice | Bob        | alice@hostname.com |Axel| False     |
| Tom   | Alice      | tom@hostname.com   |Bob| False     |

Optionally, to preserve the secret of the assignment, one can specify a password by adding the
`--password` option to the command above.

### Inspecting Assignments

After generating assignments, you can inspect the assignments by either printing them to the command line, using the`show` command,
or by displaying them as a graph using the `visualize` command.

```csv
wichteln show [--password <pw>] [--show-names] <assignments.csv>
wichteln visualize [--password <pw>] [--show-names] <assignments.csv>
```

If the option `--show-names` is specified, the commands will display the names of the assigned persons, otherwise not.
If the assignment file is encrypted, you have to specify the correct password.

### Sending Assignments

> :warning: Sending mails from a python script is not well supported. Some mail providers (e.g. GMail) do not support this.

To send a mail with the assigned name to each of the participants, you can call use `send` command.
In order to send emails from this application, you need to provide a mail configuration file (in YAML format) which contains the
following information:
- *subject*: The subject of the mail.
- *body_template*: A string template that contains the message that will be sent out. It has to contain exactly two string placeholders (`%s`) for the name of the
recepient and his/her assigned wichtel.
- *sender*: Your email address
- *host*: The hostname of your mail server.
- *port*: The SMTP port of you mail server.
- *use_tls*: Wheter to use the TLS protocol or not.

Below you can see an example mail configuration:

```yaml
subject: "Secret Santa"
body_template: |
  Hi %s!
  Your wichtel is %s.
  Best,
  Santa
sender: "santa@localhost"
host: "localhost"
port: 25
use_tls: true
```
The command to send out mails is:

`wichteln send --mail-config <path> [--password <pw>] [--dry-run] <assignments.csv>`

If you have encrypted the assignments, you need to provide the correct password, otherwise your participants
won't be able to read their assigned wichtels. 
To test if the login and the mail generation works, you can use the ```--dry-run``` option. Then the emails will
be print out to the console instead of being sent to the recipients.