kramer
======

## Requirements
0. Linux (with write access to `/tmp`)
1. Python 2.7.6
2. MIT Language Modeling Toolkit

I am using SUSE running 3.11.10-17.

You may need to install [python-daemon
1.5.5](https://pypi.python.org/pypi/python-daemon/ "python-daemon"). See [PEP
3143](legacy.python.org/dev/peps/pep-3143/ "PEP 3143") for example usage.

You must install the [MIT Language Modeling
Toolkit](https://code.google.com/p/mitlm "mitlm"); the tools must be in your
`$PATH`.

## Usage

See `braind -h` for basic usage.

The brain estimates a n-gram language model. Optionally, you can set the order
(default=3) and you can specify the smoothing algorithm (default='Modified
Kneser-Ney'). Assuming `braind` is in your `$PATH`, enter

```bash
braind path/to/training/data
```

at a shell prompt. This will estimate a trigram using ModKN from the training
data and write the ARPA file to `/tmp/lm`. Then the brain will make two named
pipes, `/tmp/fifo0` and `/tmp/fifo1`, to serve as communication channels with
the n-gram server before daemonizing the process.

When the server is launched, the first thing it will do is deserialize `/tmp/lm`
into a key-value store. Obviously, this is a horribly inefficient data structure
for this purpose, but performance is not the key concern for our current work.
After the server learns a language model, the prompt will return. You can verify
the server is running by examining the output of `ps x`.

Clients can communicate with the language model server by reading/writing JSON
documents to the two named pipes. A client writes requests to `/tmp/fifo0` and
reads responses from `/tmp/fifo1`. A request is a JSON document with two fields:
`history` and `length`. `history` contains the initial prefix as an array of
strings. `length` is an integer which governs the length of the sentence to
query from the language model. The response is a JSON document with one field:
`stream`. `stream` contains the sampled sentence as an array of strings. Here is
an example using the Shakespeare corpus:

```bash
cat request
{ "history" : ["<s>", "There"], "length" : 10 }
cat request > /tmp/fifo0 && cat /tmp/fifo1
{"stream": ["is", "not", "that", ";", "for", "the", "hand", "of", "the",
"coronation"]}
```

Send a SIGTERM to kill the daemon: `kill PID`. A simple handler has been
implemented to clean up the `/tmp` scratch files.
