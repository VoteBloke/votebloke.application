import json

import requests

from generate_keys import *


def post_new_elections(signing_keys: ecdsa.SigningKey, question: str, options: list[str],
                       url: str = 'http://localhost:8080/v1/blockchain/elections'):
    data = {
        'elections': question,
        'answers': options
    }
    data = json.dumps(data)

    return requests.request(
        method='post',
        url=url,
        data=data,
        headers={'Content-type': 'application/json', 'public-key': key_to_string(signing_keys.verifying_key)}
    )


def create_account(url='http://localhost:8080/v1/blockchain/accounts/create'):
    return generate_keys()


def get_active_elections(url='http://localhost:8080/v1/blockchain/transactions/elections'):
    return requests.request(method='get', url=url)


def cast_vote(elections, option, url='http://localhost:8080/v1/blockchain/vote'):
    data = {
        'answer': option,
        'electionsTransactionId': elections
    }

    data = json.dumps(data)

    return requests.request(
        method='post',
        url=url,
        data=data,
        headers={'Content-type': 'application/json'}
    )
