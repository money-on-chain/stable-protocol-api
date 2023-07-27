# Stable Protocol API

API list operations of the users.

### Usage

Requirements:

* Python 3.9+

```
# Install the requirements:
pip install -r requirements.txt

# Configure the location of your MongoDB database:
copy .example.env .env

# Edit .env file and change settings point Mongo DB uris 

# Start the service
uvicorn api.app:app --reload
```

### Interactive API docs

Go to http://localhost:8000/


### Docker (Recommended)

Build, change path to correct environment

```
docker build -t stable_protocol_api -f Dockerfile .
```

Run

```
docker run -d \
--name stable_protocol_api_roc_mainnet \
--env APP_MONGO_URI=mongodb://localhost:27017 \
--env APP_MONGO_DB=roc_mainnet \
--env BACKEND_CORS_ORIGINS=["*"] \
--env ALLOWED_HOSTS=["*"] \
stable_protocol_api
```


