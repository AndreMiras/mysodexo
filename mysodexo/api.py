#!/usr/bin/env python3
import os
from pprint import pprint
from typing import Tuple

import requests

from mysodexo.constants import (
    BASE_URL,
    DEFAULT_DEVICE_UID,
    DEFAULT_LANG,
    DEFAULT_OS,
    GET_CARDS_ENDPOINT,
    GET_DETAIL_CARD,
    JSON_RESPONSE_OK_CODE,
    JSON_RESPONSE_OK_MSG,
    LOGIN_ENDPOINT,
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


def login(email: str, password: str) -> Tuple[requests.sessions.Session, dict]:
    """Logins with credentials and returns session and account info."""
    endpoint = get_full_endpoint_url(LOGIN_ENDPOINT)
    session = requests.session()
    data = {
        "username": email,
        "pass": password,
        "deviceUid": DEFAULT_DEVICE_UID,
        "os": DEFAULT_OS,
    }
    response = session.post(
        endpoint, json=data, cert=REQUESTS_CERT, headers=REQUESTS_HEADERS
    )
    json_response = response.json()
    handle_code_msg(json_response)
    account_info = json_response["response"]
    return session, account_info


def get_cards(session: requests.sessions.Session, dni: str) -> list:
    """Returns cards list and details using the session provided."""
    endpoint = get_full_endpoint_url(GET_CARDS_ENDPOINT)
    data = {
        "dni": dni,
    }
    response = session.post(
        endpoint, json=data, cert=REQUESTS_CERT, headers=REQUESTS_HEADERS
    )
    json_response = response.json()
    handle_code_msg(json_response)
    card_list = json_response["response"]["listCard"]
    return card_list


def get_detail_card(
    session: requests.sessions.Session, card_number: str
) -> dict:
    """Returns card details."""
    endpoint = get_full_endpoint_url(GET_DETAIL_CARD)
    data = {
        "cardNumber": card_number,
    }
    response = session.post(
        endpoint, json=data, cert=REQUESTS_CERT, headers=REQUESTS_HEADERS
    )
    json_response = response.json()
    handle_code_msg(json_response)
    details = json_response["response"]["cardDetail"]
    return details


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
