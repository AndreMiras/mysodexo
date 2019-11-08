#!/usr/bin/env python3
import argparse
import os
import pickle
from getpass import getpass
from typing import Tuple

import requests
from appdirs import user_cache_dir

from mysodexo import api
from mysodexo.constants import APPLICATION_NAME, SESSION_CACHE_FILENAME


def prompt_login() -> Tuple[str, str]:
    """Prompts user for credentials and the returns them as a tuple."""
    email = input("email: ")
    password = getpass("password: ")
    return (email, password)


def get_session_cache_path() -> str:
    return os.path.join(
        user_cache_dir(appname=APPLICATION_NAME), SESSION_CACHE_FILENAME
    )


def get_cached_session_info() -> Tuple[
    requests.cookies.RequestsCookieJar, str
]:
    """Returns session and DNI from cache."""
    session_cache_path = get_session_cache_path()
    with open(session_cache_path, "rb") as f:
        cached_session_info = pickle.load(f)
    cookies = cached_session_info["cookies"]
    dni = cached_session_info["dni"]
    return (cookies, dni)


def cache_session_info(
    cookies: requests.cookies.RequestsCookieJar, dni: str
) -> None:
    """Stores session info to cache."""
    session_cache_path = get_session_cache_path()
    cached_session_info = {
        "cookies": cookies,
        "dni": dni,
    }
    os.makedirs(os.path.dirname(session_cache_path), exist_ok=True)
    with open(session_cache_path, "wb") as f:
        pickle.dump(cached_session_info, f)


def login() -> Tuple[requests.sessions.Session, str]:
    """Logins and stores session info to cache."""
    email, password = prompt_login()
    session, account_info = api.login(email, password)
    dni = account_info["dni"]
    cache_session_info(session.cookies, dni)
    return (session, dni)


def get_session_or_login() -> Tuple[requests.sessions.Session, str]:
    """Retrieves session from cache or prompts login."""
    try:
        cookies, dni = get_cached_session_info()
        session = requests.session()
        session.cookies.update(cookies)
    except FileNotFoundError:
        session, dni = login()
    return session, dni


def print_balance(cards):
    """Prints per card balance."""
    for card in cards:
        pan = card["pan"]
        details = card["_details"]
        balance = details["cardBalance"]
        print(f"{pan}: {balance}")


def process_balance():
    session, dni = get_session_or_login()
    cards = api.get_cards(session, dni)
    for card in cards:
        card_number = card["cardNumber"]
        details = api.get_detail_card(session, card_number)
        card["_details"] = details
    print_balance(cards)


def main():
    parser = argparse.ArgumentParser(
        description="MySodexo Command Line Interface"
    )
    parser.add_argument(
        "--login", action="store_true", help="Logins and store session.",
    )
    parser.add_argument(
        "--balance",
        action="store_true",
        help="Returns account balance per card",
    )
    args = parser.parse_args()
    if args.login:
        login()
    elif args.balance:
        process_balance()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
