#!/usr/bin/env python

import model
import unittest

class TestNgram(unittest.TestCase):

  def setUp(self):
    self.lm = model.Ngram()

  def test_header(self):
    h = len(self.lm._arpa_model_header)
    b = len(self.lm._ngram_buckets)
    self.assertEqual(h, b)

  def test_cp(self):
    for i, n in enumerate(self.lm._arpa_model_header):
      if i > 0:
        s = sum([len(v) for k, v in self.lm._ngram_buckets[i].items()])
        self.assertEqual(s, n)

if __name__ == '__main__':
  unittest.main()
