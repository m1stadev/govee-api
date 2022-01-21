# Govee API

[![License](https://img.shields.io/github/license/m1stadev/govee-api)](https://github.com/m1stadev/govee-api/blob/master/LICENSE)
[![Stars](https://img.shields.io/github/stars/m1stadev/govee-api)](https://github.com/m1stadev/govee-api/stargazers)
[![LoC](https://img.shields.io/tokei/lines/github/m1stadev/govee-api)](https://github.com/m1stadev/govee-api)

An API for simplifying interacting with WiFi-enabled [Govee](https://us.govee.com/) LED products using the [Govee API](https://govee-public.s3.amazonaws.com/developer-docs/GoveeAPIReference.pdf).

## Running
To host, follow these steps:

1. Create a virtual env and install dependencies:

        python3 -m venv --upgrade-deps env && source env/bin/activate
        pip3 install -Ur requirements.txt

2. Set your Govee API key in the `GOVEE_API_KEY` environment variable.
    - Instructions on how to get an API key can be found [here](https://twitter.com/GoveeOfficial/status/1383962664217444353?s=20).

3. Start your instance:

        gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:80

## API Documentation
API documentation can be found at `http://{IP}:80/docs`, replacing `{IP}` with either `localhost` or the IP address of the device you're hosting Govee API on.

## Support

For any questions/issues you have, join my [Discord](https://m1sta.xyz/discord).
