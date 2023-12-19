"""Initialize tests."""


from custom_components.delios.client import DeliosClient


class FakeClient:
    """Fake client class."""

    # pylint: disable=unused-argument
    async def fake_login(self, username: str, password: str) -> bool:
        """Fake login method."""
        return True


DeliosClient.login = FakeClient.fake_login
