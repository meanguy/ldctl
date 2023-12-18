import functools
from collections.abc import AsyncGenerator
from datetime import timedelta
from urllib.parse import parse_qs, urlparse

import aiohttp
from pylons import retry


class HttpError:
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message


def retry_api_request(max_attempts: int) -> retry.RetryStrategy:
    def wrapper(tries: int, exception: Exception) -> bool:
        if tries >= max_attempts:
            return False

        if isinstance(exception, (HttpError, aiohttp.ClientResponseError)):
            if exception.status in {429, 503}:
                return True

        return False

    return wrapper


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

    async def get_members_page(
        self,
        offset: int,
        limit: int | None = None,
    ) -> dict:
        url = f"https://app.launchdarkly.com/api/v2/members"
        params = {"offset": offset}
        if limit is not None:
            params["limit"] = limit

        return await self._make_get_request(url, params)

    async def get_members(self) -> AsyncGenerator[dict, None]:
        assert self._session is not None
        offset = 0
        limit = None

        while True:
            members_page = await self.get_members_page(offset, limit)

            for item in members_page.get("items", []):
                yield item

            if next_page := members_page.get("_links", {}).get("next", None):
                next_url = urlparse(next_page["href"])
                query_params = parse_qs(next_url.query)

                offset = int(query_params["offset"][0])
                limit = int(query_params["limit"][0])
            else:
                break

    async def get_custom_role(self, role_id: str) -> dict:
        return await self._make_get_request(f"https://app.launchdarkly.com/api/v2/custom-roles/{role_id}", {})

    @retry.retryable(
        retry_strategy=retry_api_request(max_attempts=5),
        backoff_strategy=retry.exponential_backoff(timedelta(milliseconds=100), 1.5),
    )
    async def _make_get_request(self, url: str, params: dict) -> dict:
        assert self._session is not None
        async with self._session.get(url, params=params) as resp:
            if resp.status > 399:
                raise Exception(f"Failed to get members page: {resp.status} {await resp.text()}")

            return await resp.json()
