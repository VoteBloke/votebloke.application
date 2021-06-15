import json

import requests

import cryptography_wrappers
from cryptography.hazmat.primitives.asymmetric import ec


# Get requests
def get_unsigned_transactions(
        url: str = 'http://localhost:8080/v1/blockchain/transactions/unsigned') -> \
        requests.Response:
    """
    Returns all unsigned transactions. Unsigned transactions don't count as output transactions,
    eg. unsigned elections will not accept votes, unsigned vote
    will not be counted towards active elections, etc...

    :param url: the api endpoint
    :return: the response from the server
    """
    return requests.get(url=url)


def get_active_elections(
        url: str = 'http://localhost:8080/v1/blockchain/transactions/elections') -> \
        requests.Response:
    """
    Returns all active elections (elections accepting votes).

    :param url: the api endpoint
    :return: the response from the server
    """
    return requests.get(url=url)


def get_output_transactions(
        url: str = 'http://localhost:8080/v1/blockchain/transactions') -> requests.Response:
    """
    Returns all outgoing, unconsumed transactions in the chain. Tally objects will be part of
    this. These transactions
    count when posting a new Transaction (eg. a vote in the unconsumed transaction will be
    counted by a newly
    posted tally, etc...).

    :param url: the api endpoint
    :return: the response from the server
    """
    return requests.get(url=url)


# Post requests
def post_new_elections(signing_keys: ec.EllipticCurvePrivateKey, question: str, options: list,
                       url: str = 'http://localhost:8080/v1/blockchain/elections') -> \
        requests.Response:
    data = {'elections': question, 'answers': options}
    data = json.dumps(data)
    response = requests.post(url=url, data=data, headers={'Content-Type': 'application/json',
                                                          'public-key':
                                                              cryptography_wrappers.encode_public_key(
                                                              signing_keys)})

    if response.ok:
        elections = json.loads(response.content)
        return sign_transaction(signing_keys, transaction_id=elections['transactionId'],
                                signing_data=elections['dataToSign'])

    return response


def sign_transaction(signing_keys: ec.EllipticCurvePrivateKey, transaction_id: str,
                     signing_data: str,
                     url: str = 'http://localhost:8080/v1/blockchain/transactions/sign') -> \
        requests.Response:
    payload = {'transactionId': transaction_id,
               'signature': cryptography_wrappers.sign_data(data=signing_data, key=signing_keys)}
    payload = json.dumps(payload)

    return requests.post(url=url,
                         headers={'Accept': 'application/json', 'Content-Type': 'application/json',
                                  'public-key': cryptography_wrappers.encode_public_key(
                                      signing_keys)}, data=payload)


def cast_vote(signing_keys: ec.EllipticCurvePrivateKey, elections_transaction_id: str, option: str,
              url: str = 'http://localhost:8080/v1/blockchain/vote') -> requests.Response:
    data = {'answer': option, 'electionsTransactionId': elections_transaction_id}
    data = json.dumps(data)

    response = requests.post(url=url, data=data, headers={'Accept': 'application/json',
                                                          'Content-Type': 'application/json',
                                                          'public-key':
                                                              cryptography_wrappers.encode_public_key(
                                                              signing_keys)})

    if response.ok:
        vote = json.loads(response.content)
        return sign_transaction(signing_keys, transaction_id=vote['transactionId'],
                                signing_data=vote['dataToSign'])
    return response


def tally_elections(signing_keys: ec.EllipticCurvePrivateKey, elections_transaction_id: str,
                    url: str = 'http://localhost:8080/v1/blockchain/tally'):
    data = {'electionsTransactionId': elections_transaction_id}
    data = json.dumps(data)
    response = requests.post(url=url, data=data, headers={'Accept': 'application/json',
                                                          'Content-Type': 'application/json',
                                                          'public-key':
                                                              cryptography_wrappers.encode_public_key(
                                                              signing_keys)})
    if response.ok:
        tally = json.loads(response.content)
        return sign_transaction(signing_keys, tally['transactionId'],
                                signing_data=tally['dataToSign'])
    return response
