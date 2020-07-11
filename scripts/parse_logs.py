import markovify
import argparse
import pickle
import re
import os


message_patterns = {
    'irssi': re.compile("^(\d\d):(\d\d)\s<(?P<nick>.*?)>\s(?P<message>.*)$", re.IGNORECASE),
    'znc': re.compile("^\[(?P<time>.*?)\]\s<(?P<nick>.*?)>\s(?P<message>.*)$", re.IGNORECASE)
}


def generate_newline_corpus(source, destination, message_pat):
    logs = sorted(os.listdir(source))
    for log_file in logs:
        with open(destination, 'w') as outfile, open(os.path.join(source, log_file), 'r') as infile:
            for sentence in infile.readlines():
                match = re.match(message_pat, sentence)
                if match:
                    outfile.write(f'''{match['message']}\n''')

def train_model(source, destination, message_pat):
    logs = sorted(os.listdir(source))
    sentences = []
    for log_file in logs:
        with open(os.path.join(source, log_file), 'r') as fh:
            for sentence in fh.readlines():
                match = re.match(message_pat, sentence)
                if match:
                    sentences.append(match['message'])
    text = '\n'.join(sentence for sentence in sentences)

    with open(destination, 'wb') as fh:
        model = markovify.NewlineText(text, retain_original=False)
        pickle.dump(model, fh)

def main(args):
    if args.log_type not in (message_patterns.keys()):
        raise ValueError(f'Log format {args.log_type} not supported')
    if args.train_model:
        train_model(args.source, args.destination, message_patterns[args.log_type])
    else:
        generate_newline_corpus(args.source, args.destination, message_patterns[args.log_type])





parser = argparse.ArgumentParser(description='A highly inefficient script to generate a markovify-friendly training corpus')
parser.add_argument('--source', help='source path (ZNC logs dir)', type=str)
parser.add_argument('--destination', help='destination path. Textfile, or pickled blob (if --train-model)', type=str)
parser.add_argument('--log-type', help='Type of log to parse (znc, irssi)', default='irssi', type=str)
parser.add_argument('--train-model', help='if True, pickle a compressed markovify blob (faster load time & inference)', dest='train_model', action='store_true')
parser.set_defaults(train_model=False)

if __name__ == '__main__':
    args = parser.parse_args()
    main(args)

