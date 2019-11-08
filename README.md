# Mysodexo Python client

[![Build Status](https://travis-ci.com/AndreMiras/mysodexo.svg?branch=develop)](https://travis-ci.com/AndreMiras/mysodexo)
[![Coverage Status](https://coveralls.io/repos/github/AndreMiras/mysodexo/badge.svg?branch=develop)](https://coveralls.io/github/AndreMiras/mysodexo?branch=develop)
[![PyPI version](https://badge.fury.io/py/mysodexo.svg)](https://badge.fury.io/py/mysodexo)

A Python client for the Mysodexo [reverse engineered API](https://github.com/AndreMiras/mysodexo/blob/develop/docs/ReverseEngineering.md).


## Install & Usage
Install it with pip.
```sh
pip install mysodexo
```
Then use the command line client.
```sh
mysodexo --balance
```
Or the library.
```python
from mysodexo import api
session, account_info = api.login("foo@bar.com", "password")
dni = account_info["dni"]
cards = api.get_cards(session, dni)
card = cards[0]
card_number = card["cardNumber"]
card_details = api.get_detail_card(session, card_number)
card_details["cardBalance"]
```
