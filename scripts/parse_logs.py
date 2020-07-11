import markovify
import argparse
import pickle
import re
import os


message_patterns = {
    "irssi": re.compile(
        "^(?P<time>(\d\d):(\d\d))\s<(?P<nick>.*?)>\s(?P<message>.*)$", re.IGNORECASE
    ),
    "znc": re.compile(
        "^\[(?P<time>.*?)\]\s<(?P<nick>.*?)>\s(?P<message>.*)$", re.IGNORECASE
    ),
}


def serialize_markovify_chain(model, destination, format):
    if format == "pickle":
        with open(destination, "wb") as fh:
            pickle.dump(model, fh)
    elif format == "json":
        with open(destination, "w") as fh:
            fh.write(model.to_json())


def generate_newline_corpus(source, destination, message_pat):
    logs = sorted(os.listdir(source))
    for log_file in logs:
        with open(destination, "w") as outfile, open(
            os.path.join(source, log_file), "r"
        ) as infile:
            for sentence in infile.readlines():
                match = re.match(message_pat, sentence)
                if match:
                    outfile.write(f"""{match['message']}\n""")


def train_model(source, destination, message_pat, format):
    if format not in ("pickle", "json"):
        raise ValueError(f"Serialization error: f{format} format not supported.")
    logs = sorted(os.listdir(source))
    sentences = []
    for log_file in logs:
        with open(os.path.join(source, log_file), "r") as fh:
            for sentence in fh.readlines():
                match = re.match(message_pat, sentence)
                if match:
                    sentences.append(match["message"])
    text = "\n".join(sentence for sentence in sentences)

    model = markovify.NewlineText(text, retain_original=False)
    serialize_markovify_chain(model, destination, format)


def main(args):
    if args.log_type not in (message_patterns.keys()):
        raise ValueError(f"Log format {args.log_type} not supported")
    if args.train_model:
        format = args.train_model
        train_model(
            args.source, args.destination, message_patterns[args.log_type], format
        )
    else:
        generate_newline_corpus(
            args.source, args.destination, message_patterns[args.log_type]
        )


parser = argparse.ArgumentParser(
    description="A highly inefficient script to generate a markovify-friendly training corpus"
)
parser.add_argument("--source", help="source path (ZNC logs dir)", type=str)
parser.add_argument(
    "--destination",
    help="destination path. Textfile, or pickled blob (if --train-model)",
    type=str,
)
parser.add_argument(
    "--log-type",
    help="Type of log to parse (znc, irssi). Default: irssi",
    default="irssi",
    type=str,
)
parser.add_argument(
    "--train-model",
    help="Train a markovify chain and serialize it as either pickle or json",
    dest="train_model",
    default=None,
)
parser.set_defaults(train_model=False)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
