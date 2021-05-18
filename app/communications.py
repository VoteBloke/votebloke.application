import json

import requests

#important variables

def postNewElections(title, options, url = 'http://localhost:8080/v1/blockchain/elections') :
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

def createAccount(url = 'http://localhost:8080/v1/blockchain/accounts/create') :
    return requests.request(method = 'get', url = url)

def getActiveElections(url = 'http://localhost:8080/v1/blockchain/transactions/elections') :
    return requests.request(method = 'get', url = url)

def castVote(elections, option, url = 'http://localhost:8080/v1/blockchain/vote') :
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