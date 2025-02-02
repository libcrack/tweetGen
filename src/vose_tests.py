#!/usr/bin/env python

# LIBRARIES:
# Standard library
import math
import random
import unittest
from decimal import *
# Local application
from src.vose import *

# Common paths and error messages
valid_folder = "../corpus/valid_folder/"
invalid_folder = "../corpus/invalid_folder/"


class TestAccuracy(unittest.TestCase):
    """ unittest methods for testing the accuracy of method within vose_sampler. """

    def dbinom(self, x, n, p):
        """ Compute the probability of x successes in n flips of a coin that produces
        a head with probability p (i.e. the probability density of a Binomial RV). """
        f = math.factorial
        C = Decimal(f(n) / (f(x) * f(n-x)))
        return C * p**x * (1-p)**(n-x)

    def test_output_get_word(self):
        """Test get_words to ensure it correctly produces a list of
        words from a given corpus. """
        actual = get_words('../corpus/alice.txt')
        expected = ["alice"]
        self.assertEqual(actual, expected)

    def test_output_create_dist(self):
        """Test ProbDistribution.create_dist to ensure it correctly
        produces a uniform distribution for a list of words representing a standard die. """
        numbers_dist = sample2dist(
            ["one", "two", "three", "four", "five", "six"])
        VA_numbers = VoseAlias(numbers_dist)
        actual = VA_numbers.dist
        prob = Decimal(1)/Decimal(6)
        expected = {"one": prob, "two": prob, "three": prob,
                    "four": prob, "five": prob, "six": prob}
        self.assertEqual(actual, expected)

    def test_output_alias_generation(self):
        """Test vose_sampler.ProbDistribution.alias_generation to ensure it
        generates words with same distribution as the original corpus. This
        performs a 2-sided hypothesis test at the 1% significance level, that:
        H_0: observed proportion a randomly selected word is equal to the
            proportion seen in the original corpus (i.e. p_original == p_observed)
        H_1: p_original != p_observed
        """
        print("WARNING: There is a random element to test_output_alias_generation\n\
        so it is likely to occasionally fail, nonetheless if the alias_generation\n\
        method is working correctly failures will be very rare (testing at alpha=0.01\n\
        implies we should expect a Type I error about 1% of the time).")

        # Construct a ProbDistribution
        words = get_words('../corpus/thus.txt')
        word_dist = sample2dist(words)
        VA_words = VoseAlias(word_dist)

        # Generate sample and calculate the number of observations for a randomly selected word
        word = random.choice(list(VA_words.dist))

        n = 1000

        t = 0
        for i in range(n):
            if VA_words.alias_generation() == word:
                t += 1

        # Compute the p-value
        p_original = VA_words.dist[word]

        p_low = math.fsum([self.dbinom(x, n, p_original)
                           for x in range(t, n+1)])
        p_high = math.fsum([self.dbinom(x, n, p_original) for x in range(t+1)])

        p = 2*min(p_low, p_high)

        # Do not accept H_0 if p <= alpha
        alpha = 0.01
        self.assertGreater(p, alpha)

    def test_roundtrip(self):
        dist = {"H": Decimal(0.2), "T": Decimal(0.8)}
        VA = VoseAlias(dist)
        sample = VA.sample_n(100000)
        computed_dist = sample2dist(sample)
        self.assertAlmostEqual(
            dist.get("H"), computed_dist.get("H"), delta=0.01)
        self.assertAlmostEqual(
            dist.get("T"), computed_dist.get("T"), delta=0.01)


if __name__ == "__main__":
    unittest.main()
