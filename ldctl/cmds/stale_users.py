import json
import logging
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone

from ldctl.api import LaunchDarklyClient
from ldctl.prettier import parse_time_ago, pretty_time_ago


@dataclass
class User:
    id: str
    first_name: str
    last_name: str
    email: str
    last_seen: str

    def __str__(self) -> str:
        return f"[{self.id}] {self.first_name} {self.last_name} <{self.email}> [last seen {self.last_seen}]"


async def main(
    log: logging.Logger,
    client: LaunchDarklyClient, since: str, pretty: bool,
    ) -> int:
    now = datetime.now(timezone.utc)
    stale_cutoff_date = now - parse_time_ago(since)

    stale_users = []
    total_users_count = 0

    async with client:
        async for member in client.get_members():
            total_users_count += 1

            if not "_lastSeen" in member:
                log.debug(f"Skipping user {member["_id"]} with no last seen date")

                continue

            if member.get("role", "") in {"admin", "owner"}:
                log.debug(f"Skipping user {member["_id"]} with role {member["role"]}")

                continue

            last_seen = datetime.fromtimestamp(member["_lastSeen"] / 1000, tz=timezone.utc)
            if last_seen < stale_cutoff_date:
                stale_users.append(member)


    print(f"Found {len(stale_users)} stale users out of {total_users_count} total users", file=sys.stderr)
    
    users = []
    for stale_user in stale_users:
        time_since_seen = now - datetime.fromtimestamp(stale_user["_lastSeen"] / 1000, tz=timezone.utc)

        users.append(User(
            id=stale_user.get("_id", "unknown"),
            first_name=stale_user.get("firstName", "unknown"),
            last_name=stale_user.get("lastName", "unknown"),
            email=stale_user.get("email", "unknown"),
            last_seen=pretty_time_ago(time_since_seen),
        ))

    if pretty:
        for user in users:
            print(user)
    else:
        print(json.dumps([asdict(user) for user in users], indent=2))

    return 0
