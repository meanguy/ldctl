from ldctl.api import LaunchDarklyClient


async def main(client: LaunchDarklyClient, user_id: str) -> int:
    async with client:
        if await client.delete_user(user_id):
            print(f"Deleted user {user_id}")

            return 0
        else:
            print(f"Failed to delete user {user_id}")

            return 1
