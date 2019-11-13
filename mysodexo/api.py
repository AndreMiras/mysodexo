#!/usr/bin/env python3
import os
from pprint import pprint
from typing import Any, Dict, Tuple

import requests

from mysodexo.constants import (
    BASE_URL,
    DEFAULT_DEVICE_UID,
    DEFAULT_LANG,
    DEFAULT_OS,
    GET_CARDS_ENDPOINT,
    GET_CLEAR_PIN_ENDPOINT,
    GET_DETAIL_CARD_ENDPOINT,
    JSON_RESPONSE_OK_CODE,
    JSON_RESPONSE_OK_MSG,
    LOGIN_ENDPOINT,
    LOGIN_FROM_SESSION_ENDPOINT,
    REQUESTS_CERT,
    REQUESTS_HEADERS,
)


def get_full_endpoint_url(endpoint: str, lang: str = DEFAULT_LANG) -> str:
    endpoint = endpoint.lstrip("/")
    return f"{BASE_URL}/{lang}/{endpoint}"


def handle_code_msg(json_response: dict):
    """Raises an error if any in the `json_response`."""
    code = json_response["code"]
    msg = json_response["msg"]
    assert code == JSON_RESPONSE_OK_CODE, (code, msg)
    assert msg == JSON_RESPONSE_OK_MSG, (code, msg)


def session_post(
    session: requests.sessions.Session, endpoint: str, data: Dict[str, Any]
) -> dict:
    """
    Posts JSON `data` to `endpoint` using the `session`.
    Handles errors and returns a json response dict.
    """
    endpoint = get_full_endpoint_url(endpoint)
    response = session.post(
        endpoint, json=data, cert=REQUESTS_CERT, headers=REQUESTS_HEADERS
    )
    json_response = response.json()
    handle_code_msg(json_response)
    return json_response


def login(email: str, password: str) -> Tuple[requests.sessions.Session, dict]:
    """Logins with credentials and returns session and account info."""
    endpoint = LOGIN_ENDPOINT
    session = requests.session()
    data = {
        "username": email,
        "pass": password,
        "deviceUid": DEFAULT_DEVICE_UID,
        "os": DEFAULT_OS,
    }
    json_response = session_post(session, endpoint, data)
    account_info = json_response["response"]
    return session, account_info


def login_from_session(session: requests.sessions.Session) -> dict:
    """Logins with session and returns account info."""
    endpoint = LOGIN_FROM_SESSION_ENDPOINT
    data: Dict[str, Any] = {}
    json_response = session_post(session, endpoint, data)
    account_info = json_response["response"]
    return account_info


def get_cards(session: requests.sessions.Session, dni: str) -> list:
    """Returns cards list and details using the session provided."""
    endpoint = GET_CARDS_ENDPOINT
    data = {
        "dni": dni,
    }
    json_response = session_post(session, endpoint, data)
    card_list = json_response["response"]["listCard"]
    return card_list


def get_detail_card(
    session: requests.sessions.Session, card_number: str
) -> dict:
    """Returns card details."""
    endpoint = GET_DETAIL_CARD_ENDPOINT
    data = {
        "cardNumber": card_number,
    }
    json_response = session_post(session, endpoint, data)
    details = json_response["response"]["cardDetail"]
    return details


def get_clear_pin(session: requests.sessions.Session, card_number: str) -> str:
    """Returns card pin."""
    endpoint = GET_CLEAR_PIN_ENDPOINT
    data = {
        "cardNumber": card_number,
    }
    json_response = session_post(session, endpoint, data)
    pin = json_response["response"]["clearPin"]["pin"]
    return pin


def main():
    email = os.environ.get("EMAIL")
    password = os.environ.get("PASSWORD")
    session, account_info = login(email, password)
    print("account info:")
    pprint(account_info)
    dni = account_info["dni"]
    cards = get_cards(session, dni)
    print("cards:")
    pprint(cards)
    card = cards[0]
    card_number = card["cardNumber"]
    details = get_detail_card(session, card_number)
    print(f"details {card_number}:")
    pprint(details)


if __name__ == "__main__":
    main()
