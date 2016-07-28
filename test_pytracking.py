import copy

import pytest

from pytracking import (
    Configuration, get_click_tracking_url, get_click_tracking_url_path,
    get_open_tracking_url_path,
    get_click_tracking_result, get_open_tracking_pixel, get_open_tracking_url,
    get_open_tracking_result)


try:
    from cryptography.fernet import Fernet
    support_crypto = True
except ImportError:
    support_crypto = False

try:
    import ipware  # noqa
    support_django = True
except ImportError:
    support_django = False

DEFAULT_URL_TO_TRACK = "https://www.bob.com/hello-world/?token=valueééé"

DEFAULT_BASE_CLICK_TRACKING_URL = "https://a.b.com/tracking/"

DEFAULT_BASE_OPEN_TRACKING_URL = "https://a.b.com/tracking/open/"

DEFAULT_ENCRYPTION_KEY = b'XdhWbQZnqCIPLBL0ViPIW2vBTsmUNxAS-7mOtTdu6ZM='

DEFAULT_METADATA = {
    "param1": "val1",
    "param3": "val3b",
    "nested": {"param2": "val2"}}

DEFAULT_DEFAULT_METADATA = {
    "key1": True,
    "keyéé": "valèèè",
    "param3": "val3"
}

DEFAULT_WEBHOOK_URL = "https://webhook.com/tracking/"

DEFAULT_REQUEST_DATA = {
    "user_agent": "Firefox",
    "user_ip": "127.0.0.1"
}

DEFAULT_CONFIGURATION = Configuration(
    webhook_url=DEFAULT_WEBHOOK_URL,
    base_open_tracking_url=DEFAULT_BASE_OPEN_TRACKING_URL,
    base_click_tracking_url=DEFAULT_BASE_CLICK_TRACKING_URL,
    default_metadata=DEFAULT_DEFAULT_METADATA)


class FakeDjangoRequest(object):
    def __init__(self):
        self.META = {}


def test_get_open_tracking_pixel():
    (pixel, mime) = get_open_tracking_pixel()
    assert len(pixel) == 68
    assert mime == "image/png"


def test_basic_get_open_tracking_url():
    url = get_open_tracking_url(
        base_open_tracking_url=DEFAULT_BASE_OPEN_TRACKING_URL)
    assert url == "https://a.b.com/tracking/open/e30="


def test_in_config_open_tracking_url():
    url = get_open_tracking_url(
        base_open_tracking_url=DEFAULT_BASE_OPEN_TRACKING_URL,
        metadata=DEFAULT_METADATA)
    path = get_open_tracking_url_path(
        url, base_open_tracking_url=DEFAULT_BASE_OPEN_TRACKING_URL)

    tracking_result = get_open_tracking_result(
        path, webhook_url=DEFAULT_WEBHOOK_URL)
    assert tracking_result.tracked_url is None
    assert tracking_result.webhook_url == DEFAULT_WEBHOOK_URL
    assert tracking_result.request_data is None
    assert tracking_result.metadata == DEFAULT_METADATA
    assert tracking_result.is_open_tracking
    assert not tracking_result.is_click_tracking


def test_embedded_open_tracking_url():
    url = get_open_tracking_url(
        base_open_tracking_url=DEFAULT_BASE_OPEN_TRACKING_URL,
        webhook_url=DEFAULT_WEBHOOK_URL,
        include_webhook_url=True,
        default_metadata=DEFAULT_DEFAULT_METADATA,
        include_default_metadata=True,
        metadata=DEFAULT_METADATA)
    path = get_open_tracking_url_path(
        url, base_open_tracking_url=DEFAULT_BASE_OPEN_TRACKING_URL)

    tracking_result = get_open_tracking_result(
        path, request_data=DEFAULT_REQUEST_DATA,
        include_default_metadata=True,
        include_webhook_url=True)

    expected_metadata = copy.copy(DEFAULT_DEFAULT_METADATA)
    expected_metadata.update(DEFAULT_METADATA)

    assert tracking_result.tracked_url is None
    assert tracking_result.webhook_url == DEFAULT_WEBHOOK_URL
    assert tracking_result.request_data == DEFAULT_REQUEST_DATA
    assert tracking_result.metadata == expected_metadata
    assert tracking_result.is_open_tracking
    assert not tracking_result.is_click_tracking


def test_basic_get_click_tracking_url():
    url = get_click_tracking_url(
        DEFAULT_URL_TO_TRACK,
        base_click_tracking_url=DEFAULT_BASE_CLICK_TRACKING_URL)
    assert url ==\
        "https://a.b.com/tracking/eyJ1cmwiOiAiaHR0cHM6Ly93d3cuYm9iLmNvbS9oZWxsby13b3JsZC8_dG9rZW49dmFsdWVcdTAwZTlcdTAwZTlcdTAwZTkifQ=="  # noqa


def test_in_config_click_tracking_url():
    url = get_click_tracking_url(
        DEFAULT_URL_TO_TRACK,
        base_click_tracking_url=DEFAULT_BASE_CLICK_TRACKING_URL,
        metadata=DEFAULT_METADATA)
    path = get_click_tracking_url_path(
        url, base_click_tracking_url=DEFAULT_BASE_CLICK_TRACKING_URL)

    tracking_result = get_click_tracking_result(
        path, webhook_url=DEFAULT_WEBHOOK_URL)
    assert tracking_result.tracked_url == DEFAULT_URL_TO_TRACK
    assert tracking_result.webhook_url == DEFAULT_WEBHOOK_URL
    assert tracking_result.request_data is None
    assert tracking_result.metadata == DEFAULT_METADATA
    assert tracking_result.is_click_tracking
    assert not tracking_result.is_open_tracking


def test_embedded_click_tracking_url():
    url = get_click_tracking_url(
        DEFAULT_URL_TO_TRACK,
        base_click_tracking_url=DEFAULT_BASE_CLICK_TRACKING_URL,
        webhook_url=DEFAULT_WEBHOOK_URL,
        include_webhook_url=True,
        default_metadata=DEFAULT_DEFAULT_METADATA,
        include_default_metadata=True,
        metadata=DEFAULT_METADATA)
    path = get_click_tracking_url_path(
        url, base_click_tracking_url=DEFAULT_BASE_CLICK_TRACKING_URL)

    tracking_result = get_click_tracking_result(
        path, request_data=DEFAULT_REQUEST_DATA,
        include_default_metadata=True,
        include_webhook_url=True)

    expected_metadata = copy.copy(DEFAULT_DEFAULT_METADATA)
    expected_metadata.update(DEFAULT_METADATA)

    assert tracking_result.tracked_url == DEFAULT_URL_TO_TRACK
    assert tracking_result.webhook_url == DEFAULT_WEBHOOK_URL
    assert tracking_result.request_data == DEFAULT_REQUEST_DATA
    assert tracking_result.metadata == expected_metadata
    assert tracking_result.is_click_tracking
    assert not tracking_result.is_open_tracking


@pytest.mark.skipif(
    not support_crypto, reason="Cryptography lib not installed")
def test_basic_encrypted_get_open_tracking_url():
    url = get_open_tracking_url(
        base_open_tracking_url=DEFAULT_BASE_OPEN_TRACKING_URL,
        encryption_bytestring_key=DEFAULT_ENCRYPTION_KEY)
    path = get_open_tracking_url_path(
        url, base_open_tracking_url=DEFAULT_BASE_OPEN_TRACKING_URL)
    key = Fernet(DEFAULT_ENCRYPTION_KEY)

    # Can decrypt without raising an exception
    value = key.decrypt(path.encode("utf-8"))
    # We can only assert if the value is truthy because the value is encrypted
    # with a different salt each time.
    assert value


@pytest.mark.skipif(
    not support_crypto, reason="Cryptography lib not installed")
def test_minimal_encrypted_get_open_tracking_url():
    url = get_open_tracking_url(
        base_open_tracking_url=DEFAULT_BASE_OPEN_TRACKING_URL,
        metadata=DEFAULT_METADATA,
        encryption_bytestring_key=DEFAULT_ENCRYPTION_KEY)
    path = get_open_tracking_url_path(
        url, base_open_tracking_url=DEFAULT_BASE_OPEN_TRACKING_URL)

    tracking_result = get_open_tracking_result(
        path,
        request_data=DEFAULT_REQUEST_DATA,
        default_metadata=DEFAULT_DEFAULT_METADATA,
        webhook_url=DEFAULT_WEBHOOK_URL,
        encryption_bytestring_key=DEFAULT_ENCRYPTION_KEY)

    expected_metadata = copy.copy(DEFAULT_DEFAULT_METADATA)
    expected_metadata.update(DEFAULT_METADATA)

    assert tracking_result.tracked_url is None
    assert tracking_result.webhook_url == DEFAULT_WEBHOOK_URL
    assert tracking_result.request_data == DEFAULT_REQUEST_DATA
    assert tracking_result.metadata == expected_metadata
    assert tracking_result.is_open_tracking
    assert not tracking_result.is_click_tracking


@pytest.mark.skipif(
    not support_crypto, reason="Cryptography lib not installed")
def test_basic_encrypted_get_click_tracking_url():
    url = get_click_tracking_url(
        DEFAULT_URL_TO_TRACK,
        base_click_tracking_url=DEFAULT_BASE_CLICK_TRACKING_URL,
        encryption_bytestring_key=DEFAULT_ENCRYPTION_KEY)
    path = get_click_tracking_url_path(
        url, base_click_tracking_url=DEFAULT_BASE_CLICK_TRACKING_URL)
    key = Fernet(DEFAULT_ENCRYPTION_KEY)

    # Can decrypt without raising an exception
    value = key.decrypt(path.encode("utf-8"))
    # We can only assert if the value is truthy because the value is encrypted
    # with a different salt each time.
    assert value


@pytest.mark.skipif(
    not support_crypto, reason="Cryptography lib not installed")
def test_minimal_encrypted_get_click_tracking_url():
    url = get_click_tracking_url(
        DEFAULT_URL_TO_TRACK,
        base_click_tracking_url=DEFAULT_BASE_CLICK_TRACKING_URL,
        metadata=DEFAULT_METADATA,
        encryption_bytestring_key=DEFAULT_ENCRYPTION_KEY)
    path = get_click_tracking_url_path(
        url, base_click_tracking_url=DEFAULT_BASE_CLICK_TRACKING_URL)

    tracking_result = get_click_tracking_result(
        path,
        request_data=DEFAULT_REQUEST_DATA,
        default_metadata=DEFAULT_DEFAULT_METADATA,
        webhook_url=DEFAULT_WEBHOOK_URL,
        encryption_bytestring_key=DEFAULT_ENCRYPTION_KEY)

    expected_metadata = copy.copy(DEFAULT_DEFAULT_METADATA)
    expected_metadata.update(DEFAULT_METADATA)

    assert tracking_result.tracked_url == DEFAULT_URL_TO_TRACK
    assert tracking_result.webhook_url == DEFAULT_WEBHOOK_URL
    assert tracking_result.request_data == DEFAULT_REQUEST_DATA
    assert tracking_result.metadata == expected_metadata
    assert tracking_result.is_click_tracking
    assert not tracking_result.is_open_tracking


@pytest.fixture
def tracking_django():
    # Must call configure before importing tracking_django
    from django.conf import settings
    settings.configure()

    from pytracking import django as tracking_django

    return tracking_django


@pytest.mark.skipif(
    not support_django, reason="Django-support lib not installed")
def test_get_django_request_data(tracking_django):
    request = FakeDjangoRequest()
    request.META["HTTP_X_REAL_IP"] = "10.10.240.22"
    request.META["HTTP_USER_AGENT"] = "Firefox"

    request_data = tracking_django.get_request_data(request)

    assert request_data == {"user_agent": "Firefox", "user_ip": "10.10.240.22"}
