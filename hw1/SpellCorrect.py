##
# Credit Zhou Yu, Dan Jurafsky, Peter Norvig
# Updated Kevin Jesse
# Open source code under MIT license
##

import math
from Datum import Datum
from Sentence import Sentence
from Corpus import Corpus
from UniformModel import UniformModel
from UnigramModel import UnigramModel
from BackoffModel import BackoffModel
from SmoothUnigramModel import SmoothUnigramModel
from SmoothBigramModel import SmoothBigramModel
from CustomModel import CustomModel
from EditModel import EditModel
from SpellingResult import SpellingResult
import types
import re, collections

class SpellCorrect:
  """Spelling corrector for sentences. Holds edit model, language model and the corpus."""

  def __init__(self, lm, corpus):
    self.languageModel = lm
    self.editModel = EditModel('data/count_1edit.txt', corpus)

  def correctSentence(self, sentence):
    """Assuming exactly one error per sentence, returns the most probable corrected sentence.
       Sentence is a list of words."""

    #print "\n" * 10, sentence

    if len(sentence) == 0:
      return []

    # Test
    if sentence[1] != 'bob': return []

    # Initialize list of canidates starting with 1 (ignore start of sentence)
    canidates = [0]
    # Dictionary to hold score for each sentence
    weights = {}

    bestSentence = sentence[:] #copy of sentence
    #bestScore = float('-inf')

    # Assume initial Sentece is correct (i.e. no errors)
    bestScore = self.languageModel.score(bestSentence)
    key = ' '.join(word for word in bestSentence)
    weights[key] = float(bestScore)

    for i in xrange(1, len(sentence) - 1): #ignore <s> and </s>
      # TODO: select the maximum probability sentence here, according to the noisy channel model.
      # Tip: self.editModel.editProbabilities(word) gives edits and log-probabilities according to your edit model.
      #      You should iterate through these values instead of enumerating all edits.
      # Tip: self.languageModel.score(trialSentence) gives log-probability of a sentence

      # Gather all canidate edits including original word with lambda = 0.95
      tmp = self.editModel.editProbabilities(sentence[i])
      #tmp.append((word, math.log(0.95)))
      canidates.append(tmp)

      for ci in canidates[i]:
        # Modifies Sentence at i with canidate word
        bestSentence[i] = ci[0]

        print 'original = %s \n score = %s' % (sentence, self.languageModel.score(sentence))
        print 'new = %s \n score = %s + %s' % (bestSentence, self.languageModel.score(bestSentence), ci[1])

        # Hash into dictonary new setence with total probability as value
        # Form: {newSentence : Probability}
        bestScore = self.languageModel.score(bestSentence) + ci[1]
        # Hash as string convert after
        key = ' '.join(word for word in bestSentence)
        weights[key] = bestScore
        # Reset best Sentence
        bestSentence = sentence[:]

    # Test
    if(len(sentence) < 10):
      print "\n" * 10
      for w in weights.items():
        print w
      print "\n" * 5
      # Find bestSentence according to highest weight
      bestSentence = max(weights, key=weights.get)

      print 'original = ', sentence, self.languageModel.score(sentence)
      print "best match = ", bestSentence

      for c in canidates:
        print "given canidates = ", c

    return bestSentence

  def evaluate(self, corpus):  
    """Tests this speller on a corpus, returns a SpellingResult"""
    numCorrect = 0
    numTotal = 0
    testData = corpus.generateTestCases()
    for sentence in testData:
      if sentence.isEmpty():
        continue
      errorSentence = sentence.getErrorSentence()
      hypothesis = self.correctSentence(errorSentence)
      if sentence.isCorrection(hypothesis):
        numCorrect += 1
      numTotal += 1
    return SpellingResult(numCorrect, numTotal)

  def correctCorpus(self, corpus): 
    """Corrects a whole corpus, returns a JSON representation of the output."""
    string_list = [] # we will join these with commas,  bookended with []
    sentences = corpus.corpus
    for sentence in sentences:
      uncorrected = sentence.getErrorSentence()
      corrected = self.correctSentence(uncorrected)
      word_list = '["%s"]' % '","'.join(corrected)
      string_list.append(word_list)
    output = '[%s]' % ','.join(string_list)
    return output

def main():
  """Trains all of the language models and tests them on the dev data. Change devPath if you
     wish to do things like test on the training data."""

  trainPath = 'data/tagged-train.dat'
  trainingCorpus = Corpus(trainPath)

  devPath = 'data/tagged-dev.dat'
  devCorpus = Corpus(devPath)

  print 'Unigram Language Model: ' 
  unigramLM = UnigramModel(trainingCorpus)
  unigramSpell = SpellCorrect(unigramLM, trainingCorpus)
  unigramOutcome = unigramSpell.evaluate(devCorpus)
  print str(unigramOutcome)

  print 'Uniform Language Model: '
  uniformLM = UniformModel(trainingCorpus)
  uniformSpell = SpellCorrect(uniformLM, trainingCorpus)
  uniformOutcome = uniformSpell.evaluate(devCorpus) 
  print str(uniformOutcome)

  '''

  print 'Smooth Unigram Language Model: ' 
  smoothUnigramLM = SmoothUnigramModel(trainingCorpus)
  smoothUnigramSpell = SpellCorrect(smoothUnigramLM, trainingCorpus)
  smoothUnigramOutcome = smoothUnigramSpell.evaluate(devCorpus)
  print str(smoothUnigramOutcome)

  print 'Smooth Bigram Language Model: '
  smoothBigramLM = SmoothBigramModel(trainingCorpus)
  smoothBigramSpell = SpellCorrect(smoothBigramLM, trainingCorpus)
  smoothBigramOutcome = smoothBigramSpell.evaluate(devCorpus)
  print str(smoothBigramOutcome)

  print 'Backoff Language Model: '
  backoffLM = BackoffModel(trainingCorpus)
  backoffSpell = SpellCorrect(backoffLM, trainingCorpus)
  backoffOutcome = backoffSpell.evaluate(devCorpus)
  print str(backoffOutcome)

  print 'Custom Language Model: '
  customLM = CustomModel(trainingCorpus)
  customSpell = SpellCorrect(customLM, trainingCorpus)
  customOutcome = customSpell.evaluate(devCorpus)
  print str(customOutcome)
  
  '''

if __name__ == "__main__":
    main()
