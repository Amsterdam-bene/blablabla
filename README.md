![](https://github.com/Amsterdam-bene/blablabla/workflows/build/badge.svg)

A chatbot service bene.

# Status

Work in progress.
Once the code is a bit more stable, `master` will be protected and changes will only
be allowed by PR.

# Getting started

Install the development deps with:
```
python3 -m venv venv
pip install -r dev-requirements.txt
pip install -e .
```

# Example usage

Spin up an instance of the service with
```bash
gunicorn "api:from_corpus('input.txt')"
```
Where `input.txt` is a `\n` terminated corpus of sentences used to build 
a markov chain.
Alternatively use `"api:from_picke(<pickle file>)"` to load a pre-trained model. 


## Endpoints

The `/bot/query` endpoint expects a POST with headers and payload
as described in [https://github.com/Amsterdam-bene/poe-component-irc-plugin-recallback](https://github.com/Amsterdam-bene/poe-component-irc-plugin-recallback)

The `text` field will be used to sample from the bot and generate a sentence.
For example
```bash
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"_meta": {"api_version": 1}, "text": "Antani", "nick": "Rocco", "sender": "Rocco!~rtanica@unaffiliated/rocco", "my_own_nick": "DeBot", "channel": "##horsing-around"}' \
  ${uri}/bot/query
```
Should return a reply along the lines of
```bash
{"reply": "Tarapia sulla supercazzola con scappellamento a destra o sinistra?"}
```

The `/health` endpoints answers `GET` requests with the service status, and bot info.
For example
```bash
curl ${uri}/bot/health
```
Should return 
```bash
{"status": "OK"}
```

# Data preparation & training

TBC

# Deployment

YOLO with a dash of github actions.

# Gotchas and limitations

TBC