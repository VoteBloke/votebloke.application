import json

import requests

#important variables

def post_new_elections(title, options, url ='http://localhost:8080/v1/blockchain/elections') :
    data = {
        'elections' : title,
        'answers' : options
    }
    data = json.dumps(data)

    return requests.request(
        method = 'post',
        url = url,
        data = data,
        headers = {'Content-type': 'application/json'}
    )

def create_account(url ='http://localhost:8080/v1/blockchain/accounts/create') :
    return requests.request(method = 'get', url = url)

def get_active_elections(url ='http://localhost:8080/v1/blockchain/transactions/elections') :
    return requests.request(method = 'get', url = url)

def cast_vote(elections, option, url ='http://localhost:8080/v1/blockchain/vote') :
    data = {
        'answer': option,
        'electionsTransactionId': elections
    }

    data = json.dumps(data)

    return requests.request(
        method = 'post',
        url = url,
        data = data,
        headers = {'Content-type': 'application/json'}
    )