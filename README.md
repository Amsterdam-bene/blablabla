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

See [Data preparation and training](#data-preparation--training) for more details on how to generate both files.

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

The `/health` endpoint answers `GET` requests with the service status, and bot info.
For example
```bash
curl ${uri}/bot/health
```
Should return 
```bash
{"status": "OK"}
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
python scripts/parse_logs.py --train-model --source data/ --destination model.pickle 
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
 * While training is quick, inference latency is high when sampling with `strict=False` (our default). See https://github.com/jsvine/markovify/blob/master/markovify/text.py#L245 
 * The bot does not support multi channel / multi datasets (yet).