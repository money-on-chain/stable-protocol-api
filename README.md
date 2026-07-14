# Stable Protocol API

API list operations of the users dapp. This is a requirement for [stable-protocol-interface](https://github.com/money-on-chain/stable-protocol-interface), this service list operations of the users.

### Usage

Requirements:

* Python 3.9+
* Mongo DB installed also DB, User & pass created
* [Stable-protocol-indexer](https://github.com/money-on-chain/stable-protocol-indexer)Protocol Indexer installed & Running in the same Mongo DB

```
# Install the requirements:
pip install -r requirements.txt

# Configure the location of your MongoDB database:
cp .example.env .env

# Edit .env file and change settings point Mongo DB uris 

# Start the service
uvicorn api.app:app --reload
```

### Interactive API docs

Go to http://localhost:8000/


### Deployed environments


| Environment   | Project | URL                                                    | 
|---------------|---------|--------------------------------------------------------|
| Testnet       | MOC     | https://api-operations-testnet.moneyonchain.com/       |
| Mainnet       | MOC     | https://api-operations.moneyonchain.com/               |

### Docker (Recommended)

Build, change path to correct environment

```
docker build -t stable_protocol_api -f Dockerfile.api .
```

Run

```
docker run -d \
--name stable_protocol_api_roc_mainnet \
--env APP_MONGO_URI=mongodb://localhost:27017 \
--env APP_MONGO_DB=roc_mainnet \
--env BACKEND_CORS_ORIGINS='["*"]' \
--env ALLOWED_HOSTS='["api-operations.moneyonchain.com"]' \
--env VENDOR_ADDRESS=0xC61820bFB8F87391d62Cd3976dDc1d35e0cf7128 \
--env COMMISSION_SPLITTER_V2=0xce4548BC0b865197D94E15a5440299398aB9d32E
stable_protocol_api
```

`BACKEND_CORS_ORIGINS` and `ALLOWED_HOSTS` must be JSON arrays of strings, and they protect two different things:

- `BACKEND_CORS_ORIGINS` controls which browser origins may read this API's responses. This API is public, read-only, and never sets cookies or reads `Authorization` headers (CORS credentials are always disabled), so `["*"]` is an acceptable value — needed because the dapp frontend is deployed to IPFS and can be viewed through any gateway (`ipfs.io`, `dweb.link`, a self-hosted gateway, etc.), so its origin can't be pinned to a fixed list.
- `ALLOWED_HOSTS` is unrelated to the frontend's origin — it's the `Host` header this backend itself will accept. It must always be the API's own real hostname(s) for that environment (e.g. `api-operations.moneyonchain.com`), **never `["*"]`**, regardless of how open `BACKEND_CORS_ORIGINS` is.


