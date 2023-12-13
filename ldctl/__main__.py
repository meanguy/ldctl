import asyncio
import functools
import json
import pprint
import sys
from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator

import aiohttp
import click


def coroutine(func):
    @functools.wraps(func)
    def start(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return start


def _parse_time_since(s: str) -> timedelta:
    if s.endswith("d"):
        return timedelta(days=int(s[:-1]))
    elif s.endswith("w"):
        return timedelta(weeks=int(s[:-1]))
    elif s.endswith("m"):
        return timedelta(minutes=int(s[:-1]))
    elif s.endswith("h"):
        return timedelta(hours=int(s[:-1]))
    else:
        raise ValueError(f"invalid time since: {s}")


async def _get_members_page(session: aiohttp.ClientSession, offset: int) -> dict:
    async with session.get(f"https://app.launchdarkly.com/api/v2/members?offset={offset}") as resp:
        return await resp.json()


async def _get_members(session: aiohttp.ClientSession) -> AsyncGenerator[dict, None]:
    offset = 0

    while True:
        members_page = await _get_members_page(session, offset)

        if items := members_page.get("items", None):
            for item in items:
                yield item

        if next_offset := members_page.get("_links", {}).get("next", None):
            offset = next_offset.get("offset", None)
        else:
            break


def _launchdarkly_session(api_key: str) -> aiohttp.ClientSession:
    headers = {
        "Authorization": api_key,
        "Accept": "application/json",
    }

    return aiohttp.ClientSession(headers=headers)


@click.group()
@click.option("--api-key", required=True, help="LaunchDarkly API key")
@click.pass_context
def main(ctx: click.Context, api_key: str) -> int:
    ctx.ensure_object(dict)

    ctx.obj["api_key"] = api_key

    return 0


@main.command("stale-users")
@click.option("--since", default="180d", help="Time since last seen")
@click.option("--pretty/--no-pretty", default=False, help="Pretty print")
@click.pass_context
@coroutine
async def stale_users(ctx: click.Context, since: str, pretty: bool) -> int:
    now = datetime.now(timezone.utc)
    stale_users_date = now - _parse_time_since(since)

    async with _launchdarkly_session(ctx.obj["api_key"]) as session:
        stale_users = []

        async for member in _get_members(session):
            last_seen = datetime.fromtimestamp(member.get("_lastSeen", now) / 1000, tz=timezone.utc)
            if last_seen < stale_users_date:
                stale_users.append(member)

    if not pretty:
        print(json.dumps(stale_users, indent=2))
    else:
        for stale_user in stale_users:
            id_ = stale_user.get("_id", "unknown")
            first_name = stale_user.get("firstName", "unknown")
            last_name = stale_user.get("lastName", "unknown")
            email = stale_user.get("email", "unknown")
            time_since_seen = now - datetime.fromtimestamp(
                stale_user.get("_lastSeen", now) / 1000, tz=timezone.utc
            )

            print(f"[{id_}] {first_name} {last_name} <{email}> [last seen {time_since_seen.days}d ago]")

    return 0


@main.command("delete-user")
@click.argument("user_id")
@click.pass_context
@coroutine
async def delete_user(ctx: click.Context, user_id: str) -> int:
    async with _launchdarkly_session(ctx.obj["api_key"]) as session:
        async with session.delete(f"https://app.launchdarkly.com/api/v2/members/{user_id}") as resp:
            if resp.status == 204:
                print(f"Deleted user {user_id}")
                return 0
            else:
                print(f"Failed to delete user {user_id}")
                pprint.pprint(await resp.json())

                return 1


if __name__ == "__main__":
    sys.exit(main())
