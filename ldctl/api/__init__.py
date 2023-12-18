from typing import AsyncGenerator

import aiohttp


class LaunchDarklyClient:
    def __init__(self, api_key: str):
        self._headers = {
            "Authorization": api_key,
            "Accept": "application/json",
        }

        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(headers=self._headers)
        return self

    async def __aexit__(self, *args):
        assert self._session is not None
        await self._session.close()

    async def delete_user(self, user_id: str) -> bool:
        assert self._session is not None
        async with self._session.delete(f"https://app.launchdarkly.com/api/v2/members/{user_id}") as resp:
            return resp.status == 204

    async def get_members_page(self, offset: int) -> dict:
        assert self._session is not None
        async with self._session.get(f"https://app.launchdarkly.com/api/v2/members?offset={offset}") as resp:
            return await resp.json()

    async def get_members(self) -> AsyncGenerator[dict, None]:
        assert self._session is not None
        offset = 0

        while True:
            members_page = await self.get_members_page(offset)

            if items := members_page.get("items", None):
                for item in items:
                    yield item

            if next_offset := members_page.get("_links", {}).get("next", None):
                offset = next_offset.get("offset", None)
            else:
                break
