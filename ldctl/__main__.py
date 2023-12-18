import asyncio
import functools
import os
import sys
from random import choices

import click

from ldctl.api import LaunchDarklyClient
from ldctl.logger import configure_logger


def coroutine(func):
    @functools.wraps(func)
    def start(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return start


@click.group()
@click.option("--api-key", default="", help="LaunchDarkly API key")
@click.option(
    "--log-level",
    default="warning",
    type=click.Choice(["debug", "info", "warning", "error", "critical"]),
    help="Log level",
)
@click.pass_context
def main(
    ctx: click.Context,
    api_key: str,
    log_level: str,
) -> int:
    """
    LaunchDarkly CLI tool for administrative tasks.
    """
    ctx.ensure_object(dict)

    if not api_key:
        api_key = os.environ.get("LD_API_KEY", "")

    if not api_key:
        api_key = click.prompt("LaunchDarkly API key")

    ctx.obj.update(
        {
            "logger": configure_logger(log_level.upper()),
            "api_client": LaunchDarklyClient(api_key),
        }
    )

    return 0


@main.command("add-environment")
@click.argument("project_key")
@click.pass_context
@coroutine
async def add_environment(ctx: click.Context, project_key: str) -> int:
    """
    Add an environment to a project.

    Examples:
        ldctl add-environment my-project
    """
    from ldctl.cmds import add_environment

    return await add_environment.main(ctx.obj["api_client"], project_key)


@main.command("stale-users")
@click.option("--since", default="180d", help="Time since last seen")
@click.option("--pretty/--no-pretty", default=False, help="Pretty print")
@click.pass_context
@coroutine
async def stale_users(ctx: click.Context, since: str, pretty: bool) -> int:
    """
    List stale users.

    Examples:

        ldctl stale-users

        ldctl stale-users --since 30d

        ldctl stale-users --pretty
    """
    from ldctl.cmds import stale_users

    return await stale_users.main(ctx.obj["logger"], ctx.obj["api_client"], since, pretty)


@main.command("delete-user")
@click.argument("user_id")
@click.pass_context
@coroutine
async def delete_user(ctx: click.Context, user_id: str) -> int:
    """
    Delete a user.

    Examples:
        ldctl delete-user 00005313988494ac1a311f11
    """
    from ldctl.cmds import delete_user

    return await delete_user.main(ctx.obj["api_client"], user_id)


if __name__ == "__main__":
    sys.exit(main())
