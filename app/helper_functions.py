import json

def parse_active_elections(response_json) :
    opts = json.loads(response_json.text)

    res = [{'label': i['entryMetadata']['question'][0], 'value': i['transactionId']} for i in opts]

    return res