from unittest import mock

import pytest
import requests

from mysodexo import api
from mysodexo.constants import JSON_RESPONSE_OK_CODE, JSON_RESPONSE_OK_MSG


def test_get_full_endpoint_url():
    assert (
        api.get_full_endpoint_url(endpoint="endpoint1")
        == "https://sodexows.mo2o.com/en/endpoint1"
    )
    assert (
        api.get_full_endpoint_url(endpoint="endpoint2", lang="es")
        == "https://sodexows.mo2o.com/es/endpoint2"
    )


def test_handle_code_msg_ok():
    json_response = {
        "code": JSON_RESPONSE_OK_CODE,
        "msg": JSON_RESPONSE_OK_MSG,
    }
    assert api.handle_code_msg(json_response) is None


@pytest.mark.parametrize(
    "code,msg",
    [
        (mock.sentinel, mock.sentinel),
        (JSON_RESPONSE_OK_CODE, mock.sentinel),
        (mock.sentinel, JSON_RESPONSE_OK_MSG),
    ],
)
def test_handle_code_msg_error(code, msg):
    """Any code/msg that's not matching should raise an exception."""
    json_response = {
        "code": code,
        "msg": msg,
    }
    with pytest.raises(AssertionError) as ex_info:
        api.handle_code_msg(json_response)
    assert ex_info.value.args == ((code, msg),)


def test_login():
    email = "foo@bar.com"
    password = "password"
    response = mock.sentinel
    with mock.patch("requests.sessions.Session.post", autospec=True) as m_post:
        m_post.return_value.json.return_value = {
            "code": JSON_RESPONSE_OK_CODE,
            "msg": JSON_RESPONSE_OK_MSG,
            "response": response,
        }
        session, account_info = api.login(email, password)
    assert isinstance(session, requests.sessions.Session)
    assert account_info == response
    assert m_post.call_count == 1


def test_get_cards():
    dni = mock.ANY
    session = mock.Mock(spec=requests.sessions.Session)
    s_card_list = mock.sentinel
    session.post.return_value.json.return_value = {
        "code": JSON_RESPONSE_OK_CODE,
        "msg": JSON_RESPONSE_OK_MSG,
        "response": {"listCard": s_card_list},
    }
    card_list = api.get_cards(session, dni)
    assert card_list == s_card_list


def test_get_detail_card():
    card_number = mock.ANY
    session = mock.Mock(spec=requests.sessions.Session)
    s_details = mock.sentinel
    session.post.return_value.json.return_value = {
        "code": JSON_RESPONSE_OK_CODE,
        "msg": JSON_RESPONSE_OK_MSG,
        "response": {"cardDetail": s_details},
    }
    details = api.get_detail_card(session, card_number)
    assert details == s_details


def test_main():
    email = "foo@bar.com"
    password = "password"
    credentials = {
        "EMAIL": email,
        "PASSWORD": password,
    }
    m_session = mock.Mock()
    m_dni = mock.Mock()
    card_number = mock.Mock()
    cards = [{"cardNumber": card_number}]
    account_info = {"dni": m_dni}
    with mock.patch.dict("os.environ", credentials), mock.patch(
        "mysodexo.api.login", return_value=(m_session, account_info)
    ) as m_login, mock.patch(
        "mysodexo.api.get_cards", return_value=cards
    ) as m_get_cards, mock.patch(
        "mysodexo.api.get_detail_card"
    ) as m_get_detail_card:
        api.main()
    assert m_login.call_args_list == [mock.call(email, password)]
    assert m_get_cards.call_args_list == [mock.call(m_session, m_dni)]
    assert m_get_detail_card.call_args_list == [
        mock.call(m_session, card_number)
    ]
