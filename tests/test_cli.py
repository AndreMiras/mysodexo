import pickle
import tempfile
from io import StringIO
from unittest import mock

import pytest
import requests

from mysodexo import cli


def test_prompt_login():
    s_email = mock.sentinel
    s_password = mock.sentinel
    with mock.patch(
        "mysodexo.cli.input", return_value=s_email
    ) as m_input, mock.patch(
        "mysodexo.cli.getpass", return_value=s_password
    ) as m_getpass:
        email, password = cli.prompt_login()
    assert m_input.call_args_list == [mock.call("email: ")]
    assert m_getpass.call_args_list == [mock.call("password: ")]
    assert email == s_email
    assert password == s_password


def test_get_session_cache_path():
    with mock.patch(
        "mysodexo.cli.user_cache_dir", return_value="user_cache_dir"
    ) as m_user_cache_dir:
        session_cache_path = cli.get_session_cache_path()
    assert m_user_cache_dir.call_args_list == [mock.call(appname="mysodexo")]
    assert session_cache_path == "user_cache_dir/session.cache"


def test_get_cached_session_info():
    """Cached session data is pickle.load() from file."""
    cached_session_info = {
        "cookies": {"foo": "bar"},
        "dni": "dni",
    }
    read_data = pickle.dumps(cached_session_info)
    with mock.patch("builtins.open", mock.mock_open(read_data=read_data)):
        cookies, dni = cli.get_cached_session_info()
    assert cookies == cached_session_info["cookies"]
    assert dni == cached_session_info["dni"]


def test_get_cached_session_info_file_not_found():
    """FileNotFoundError is not handled silently."""
    with mock.patch(
        "builtins.open", side_effect=FileNotFoundError
    ), pytest.raises(FileNotFoundError):
        cli.get_cached_session_info()


def test_cache_session_info():
    cookies = requests.cookies.RequestsCookieJar()
    cookies.set("foo", "bar", domain="domain.com", path="/cookies")
    dni = "dni"
    with tempfile.NamedTemporaryFile() as cache_file:
        with mock.patch(
            "mysodexo.cli.get_session_cache_path", return_value=cache_file.name
        ):
            cli.cache_session_info(cookies, dni)
            cached_session_info = cli.get_cached_session_info()
    assert cached_session_info[0] == cookies
    assert cached_session_info[1] == dni


def test_login():
    m_email = mock.Mock()
    m_password = mock.Mock()
    s_session = mock.sentinel
    account_info = {"dni": "dni"}
    with tempfile.NamedTemporaryFile() as cache_file:
        with mock.patch(
            "mysodexo.cli.prompt_login", return_value=(m_email, m_password)
        ) as m_prompt_login, mock.patch(
            "mysodexo.api.login", return_value=(s_session, account_info)
        ) as m_login, mock.patch(
            "mysodexo.cli.get_session_cache_path", return_value=cache_file.name
        ):
            session, dni = cli.login()
    assert m_prompt_login.call_args_list == [mock.call()]
    assert m_login.call_args_list == [mock.call(m_email, m_password)]
    assert session == s_session
    assert dni == account_info["dni"]


def test_get_session_or_login_session():
    """Checks session cookies are used when available."""
    cookies = requests.cookies.RequestsCookieJar()
    cookies.set("foo", "bar", domain="domain.com", path="/cookies")
    s_dni = mock.sentinel
    with mock.patch(
        "mysodexo.cli.get_cached_session_info", return_value=(cookies, s_dni)
    ) as m_get_cached_session_info:
        session, dni = cli.get_session_or_login()
    assert m_get_cached_session_info.call_args_list == [mock.call()]
    assert isinstance(session, requests.sessions.Session)
    assert session.cookies == cookies
    assert dni == s_dni


def test_get_session_or_login_login():
    """The `login()` should be used when session cookies are not available."""
    s_session = mock.sentinel
    s_dni = mock.sentinel
    with mock.patch(
        "builtins.open", side_effect=FileNotFoundError
    ), mock.patch(
        "mysodexo.cli.login", return_value=(s_session, s_dni)
    ) as m_login:
        session, dni = cli.get_session_or_login()
    assert m_login.call_args_list == [mock.call()]
    assert session == s_session
    assert dni == s_dni


def test_print_balance():
    card_details = {"cardBalance": 12.34}
    cards = [{"pan": "123456******1234", "_details": card_details}]
    with mock.patch("sys.stdout", new_callable=StringIO) as m_stdout:
        cli.print_balance(cards)
    assert m_stdout.getvalue() == "123456******1234: 12.34\n"


def test_process_balance():
    m_session = mock.Mock()
    m_dni = mock.Mock()
    card_number = "0123456789012345"
    cards = [{"pan": "123456******1234", "cardNumber": card_number}]
    card_details = {"cardBalance": 12.34}
    with mock.patch(
        "mysodexo.cli.get_session_or_login", return_value=(m_session, m_dni)
    ) as m_get_session_or_login, mock.patch(
        "mysodexo.api.get_cards", return_value=cards
    ) as m_get_cards, mock.patch(
        "mysodexo.api.get_detail_card", return_value=card_details
    ) as m_get_detail_card, mock.patch(
        "sys.stdout", new_callable=StringIO
    ) as m_stdout:
        cli.process_balance()
    m_get_session_or_login.call_args_list == [mock.call()]
    m_get_cards.call_args_list == [mock.call(m_session, m_dni)]
    m_get_detail_card.call_args_list == [mock.call(m_session, card_number)]
    assert m_stdout.getvalue() == "123456******1234: 12.34\n"
