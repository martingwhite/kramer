import operator

def accumulate(iterable, func=operator.add):
  it = iter(iterable)
  total = next(it)
  yield total
  for element in it:
    total = func(total, element)
    yield total

def categorical_sample(sample_space, probabilities):
  from bisect import bisect
  from random import random
  #from itertools import accumulate

  cdistribution = list(accumulate(probabilities))
  uvariate = random() * cdistribution[-1]
  return sample_space[bisect(cdistribution, uvariate)]

class Ngram(object):
  def __init__(self, lm_file):
    from collections import defaultdict

    self._arpa_model_header = []
    self._ngram_buckets = []
    self._ngram_bw_store = {}

    with open(lm_file) as f:
      next(f) # skip 1st line
      next(f) # skip 2nd line

      for line in f:
        if not line.strip():
          break
        self._arpa_model_header.append(int(line.strip().split('=')[-1]))

      for bucket in range(len(self._arpa_model_header)):
        next(f) # skip r'\\\d+-grams:'
        ngram_cp_store = defaultdict(list) if bucket else {}
        for line in f:
          if not line.strip():
            break
          try:
            cp, ngram, bw = line.strip().split('\t')
            self._ngram_bw_store[ngram] = float(bw)
          except ValueError:
            cp, ngram = line.strip().split('\t')
          if ngram.count(' '):
            prefix, suffix = ngram.rsplit(' ', 1)
            ngram_cp_store[prefix].append((suffix, float(cp)))
          else:
            ngram_cp_store[ngram] = float(cp)
        self._ngram_buckets.append(ngram_cp_store)

  def _ngram_backoff(self, n, history):
    f = lambda x: zip(*[(k, 10 ** v) for k, v in x])

    prefix = ' '.join(history)
    if n == 1:
      s, p = f(self._ngram_buckets[0].items())
      return categorical_sample(s, p)
    elif prefix in self._ngram_buckets[n-1]:
      s, p = f(self._ngram_buckets[n-1][prefix])
      return categorical_sample(s, p)
    else:
      return self._ngram_backoff(n - 1, history[1:])

  def stream(self, history=[], length=1, n=None):
    from copy import deepcopy
    H = deepcopy(history)

    if n is None:
      n = len(self._arpa_model_header)
    elif n < 1 or n > len(self._arpa_model_header):
      raise ValueError('TODO')

    stream = []
    for i in range(length):
      stream.append(self._ngram_backoff(n, history))
      if n > 1:
        history = (H + stream)[-(n - 1):]
    return stream