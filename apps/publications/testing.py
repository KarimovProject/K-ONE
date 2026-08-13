from apps.publications.adapters import PublicationTransientError, PublishResult


class FakeTelegramChannelTransport:
    def __init__(self, fail_once: bool = False):
        self.fail_once = fail_once
        self.calls = []

    def publish(self, image_url: str, caption: str) -> PublishResult:
        self.calls.append({"image_url": image_url, "caption": caption})
        if self.fail_once and len(self.calls) == 1:
            raise PublicationTransientError("temporary test failure")
        return PublishResult(post_id="tg-test-1001", external_url="https://t.me/test/1001")


class FakeInstagramTransport:
    def __init__(self, fail_once: bool = False):
        self.fail_once = fail_once
        self.calls = []

    def publish(self, image_url: str, caption: str) -> PublishResult:
        self.calls.append({"image_url": image_url, "caption": caption})
        if self.fail_once and len(self.calls) == 1:
            raise PublicationTransientError("temporary test failure")
        return PublishResult(
            post_id="ig-test-2001",
            container_id="ig-container-2001",
            external_url="https://www.instagram.com/p/ig-test-2001/",
        )
