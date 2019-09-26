# FireflyIII N26-transactions-importer

This simple script aims to aggregate automatically the last `5 minutes` N26 transactions to Firefly every `5 minutes`

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/).

```bash
pip -r requirements.txt
```

## Configuration
### .env file or environment variables
```bash
#Firefly full url endpoint
FFIII_API_ENDPOINT="https://firefly.example.com/api/v1/transactions"
#Firefly personal Bearer token
FFIII_AUTH_TOKEN=

#N26 user credentials
N26_USER= 
N26_PASSWORD=

#N26 mapping categories language eg:
#micro-v2-savings-investments -> Savings & Investments
CAT_LANG="en"
```

## Usage

> Note: The first attempt to login in N26 will result in a notification from your phone to Validate the authentication otherwise the script will fail miserably :)

```bash
python3 main.py
```
or you can use
```bash
./start.sh loop
```
for autolooping the script every 5min

## License
[MIT](https://choosealicense.com/licenses/mit/)
