#!/usr/bin/env python3
import os
import time
import math
import requests
import json
from dotenv import load_dotenv
from datetime import datetime
from n26 import api
from n26 import config

load_dotenv();

def printLog(infos, e = ""):
    print(e)
    f = open("debug.log", "a")
    f.write('\r\n------Start Log------\r\n')
    if e:
        f.write(str(e))
        f.write('\r\n')
    f.write(json.dumps(infos))
    f.write('\r\n+++++++End Log+++++++\r\n')
    f.close()

def main(cat_mappings):
    conf = config.Config(os.getenv("N26_USER"), os.getenv("N26_PASSWORD"), 'store/n26_creds')
    client = api.Api(conf)

    #s to ms - CET Local
    now = int(time.time() * 1E3)
    # -5min
    minus5 = int(now - 3E5)
    print(minus5, now)

    response = client.get_transactions(limit=200, from_time=minus5, to_time = now)

    print(datetime.fromtimestamp(math.floor(minus5/1E3)), '-', datetime.fromtimestamp(math.floor(now/1E3)))

    transactions_payload = list()

    print("Transactions to process: " + str(len(response)))

    for transaction in response:
        category_name = mappings[next((index for (index, d) in enumerate(mappings) if d["id"] == transaction["category"]), None)]["name"]
        is_sepa = 'partnerName' in transaction

        if not 'confirmed' in transaction or 'paymentScheme' in transaction:
            continue

        try:
            transaction_time = time.strftime("%Y-%m-%d", time.localtime(transaction["confirmed"] / 1E3))

            is_debit = transaction["amount"] < 0

            payload = {
                'type': "withdrawal" if is_debit else "deposit",
                'external_id': transaction["linkId"],
                'date': transaction_time,
                'amount': abs(transaction["amount"]),
                'currency_code': transaction["currencyCode"],
                'category_name': category_name,
                'tags': ['N26 importer']
            }

            if is_sepa:
                payload["destination_name"] = transaction["partnerName"]
                if 'partnerIban' in transaction:
                    payload["destination_iban"] = transaction["partnerIban"]
                if 'referenceText' in transaction:
                    payload["description"] = transaction["referenceText"]

                payload["source_name"] = "N26" if is_debit else transaction["partnerName"]
                payload["destination_name"] = transaction["partnerName"] if is_debit else "N26"

            else:
                payload["source_name"] = "N26" if is_debit else transaction["merchantName"]
                payload["destination_name"] = transaction["merchantName"] if is_debit else "N26"
                payload["description"] = "(empty description)"

            transactions_payload.append(payload)
        except Exception as e:
            writeLog(transaction, e)

    if len(transactions_payload) == 0:
        print("Nothing to do")
        return

    data = {
        'transactions': transactions_payload
    }

    headers = {
        'Authorization': 'Bearer ' + os.getenv("FFIII_AUTH_TOKEN"),
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    try:
        r = requests.post(url = os.getenv("FFIII_API_ENDPOINT"), json = data, headers = headers)
        r.raise_for_status()
        print(r.text)
    except Exception as e:
        printLog(r.text, e)
        printLog(data)

    print("Job done")

if __name__ == "__main__":
    with open('categories/' + os.getenv("CAT_LANG") + '.json', 'r') as f:
        mappings = json.load(f)
    main(mappings)
