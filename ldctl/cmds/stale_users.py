import json
from datetime import datetime, timezone

import click

from ldctl.api import LaunchDarklyClient
from ldctl.prettier import parse_time_ago


async def main(client: LaunchDarklyClient, since: str, pretty: bool) -> int:
    now = datetime.now(timezone.utc)
    stale_users_date = now - parse_time_ago(since)

    async with client:
        stale_users = []

        async for member in client.get_members():
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
