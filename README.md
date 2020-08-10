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

Test with:
```bash
pytest 
```

# Example usage

Consider `config.toml` contains a list of channels and their associated chains or text corpus

Docker
------

```bash
docker build . -t blablabla
docker run -p 127.0.0.1:8000:8000 -v ./config.toml:/blablabla/config.toml -v /folder_with_bots/:/blablabla/bots/ blablabla
```

Native
------

Spin up an instance of the service with
```bash
gunicorn "api:from_config('config.toml')"
```


See [Data preparation and training](#data-preparation--training) for more details on how to generate model data.

## Endpoints

| Endpoint      |  Verb      |  Description               |
| ------------- | :--------- | :-----------               |
|  /bot/query   | POST       |  Query a bot               |
|  /bot/health  | GET        |  Service health (all bots) |

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

The `/bot/health` endpoint answers `GET` requests with the service status, and bot info.
For example
```bash
curl ${uri}/bot/health
```
Should return something like
```bash
{
    "status": "OK",
    "bots": {
        "##horsing-around": {
            "model": {
                "state_space_size": 608440,
                "state_size": 2,
                "parsed_sentences": null,
                "language": null,
                "bot_version": "0.1.0",
                "last_updated": "Not implemented"
            },
            "model_path": "bots/##horsing-around"
        },
        "##horsing-around-test": {
            "model": {
                "state_space_size": 608440,
                "state_size": 2,
                "parsed_sentences": null,
                "language": null,
                "bot_version": "0.1.0",
                "last_updated": "Not implemented"
            },
            "model_path": "bots/##horsing-around"
        }
    }
}
```

# Data preparation & training

The `scriptsb/parse_logs.py` script generates a corpus, that can be fed 
into a markov chain generator. It extract the message from an irc log
entry, and drops `timestamp` and `nick` portions. Note that if a `nick` if mentioned 
in the message body, it will be preserved in the training corpus.

Parse a set of irssi logs stored under `data/` with:
```bash
python scripts/parse_logs.py --source data/ --destination input.txt
```

Alternatively, `--train-model` will train an instance of `markovify.NewlineText`, and serialize it as
pickle:
```bash
python scripts/parse_logs.py --train-model pickle --source data/ --destination model.pickle 
```

or json:
```bash
python scripts/parse_logs.py --train-model json --source data/ --destination model.json
```

See 
```bash 
python scripts/parse_logs.py -h
``` 
for more info.

# Deployment

YOLO with a dash of github actions.

# Gotchas and limitations

Currently we use the [markovify](https://github.com/jsvine/markovify/) text generator.
The following conditions apply:
 * Data is read from a text / blob file and stored in memory.
 * The chain does not support updates. To add the new sentences, retraining is required
 * While training is quick, inference latency is high when sampling with `strict=False` (our default is now `strict=True`). See https://github.com/jsvine/markovify/blob/master/markovify/text.py#L245 
