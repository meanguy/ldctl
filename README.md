# ldctl

LaunchDarkly CLI for administrative tasks.

## Setup

```shell
    $ poetry env use python3.12
    $ poetry install
```

## Usage

```shell
Usage: python -m ldctl [OPTIONS] COMMAND [ARGS]...

Options:
  --api-key TEXT  LaunchDarkly API key  [required]
  --help          Show this message and exit.

Commands:
  stale-users
```

### Delete account user

```shell
Usage: python -m ldctl delete-user [OPTIONS] USER_ID

Options:
  --help  Show this message and exit.
```

### List stale account users

```shell
Usage: python -m ldctl stale-users [OPTIONS]

Options:
  --since TEXT  Time since last seen
  --pretty / --no-pretty  Pretty print
  --help        Show this message and exit.
```

