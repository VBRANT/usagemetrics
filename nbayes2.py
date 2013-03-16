from collections import defaultdict
import json


class NaiveBayes:
    '''Naïve Bayesian classifier for ViBRANT.

    Written should you want to use classifiers but not have access to them
    otherwise. These are simple to run classifiers to support WP3 and the
    analysis of Scratchpads' audiences.

    David King <d.j.king@open.ac.uk>
    For ViBRANT <http://vbrant.eu>
    March 2012 and February 2013

    License: LGPLv2
    '''

    def __init__(self):
        self.totals = defaultdict(lambda: defaultdict(float))
        self.priors = defaultdict(float)
        self.count = 0.0

    def add(self, cls, obs):
        '''Add an observation to the classifier's training data.'''
        terms = [term for term in obs.split(' ') if len(term) > 2]
        for term in terms:
            self.totals[cls][term] += 1.0
        self.priors[cls] += 1.0
        self.count += 1.0

    def save_data(self):
        '''Save trained data for next session.'''
        with open('nbayes2_totals.json', 'w', encoding='utf-8', newline='\n') \
            as json_file:
            json.dump(self.totals, json_file)
        with open('nbayes2_priors.json', 'w', encoding='utf-8', newline='\n') \
            as json_file:
            json.dump(self.priors, json_file)
        with open('nbayes2_count.json', 'w', encoding='utf-8', newline='\n') \
            as json_file:
            json.dump(self.count, json_file)

    def load_data(self):
        '''Load trained data from earlier session.'''
        with open('nbayes2_total.json', 'r', encoding='utf-8') \
            as json_file:
            self.totals = json.load(json_file)
        with open('nbayes2_priors.json', 'r', encoding='utf-8') \
            as json_file:
            self.priors = json.load(json_file)
        with open('nbayes2_count.json', 'r', encoding='utf-8') \
            as json_file:
            self.count = json.load(json_file)

    def _bayes_prob(self, cls, obs):
        '''Calculate Bayesian probabilistic.'''
        result = self.priors[cls] / self.count
        terms = [term for term in obs.split(' ') if len(term) > 2]
        for term in terms:
            freq = self.totals.get(cls).get(term, 0.5)
            result *= freq / self.priors[cls]
        return result

    def classify(self, obs):
        '''Classify an observation.'''
        candidates = {cls: self._bayes_prob(cls, obs) for cls in self.priors}
        # print('{} for {}'.format(candidates, obs))
        return max(candidates, key=lambda cls: candidates[cls])

if __name__ == '__main__':
    nb = NaiveBayes()
    nb.add('research/edu', 'the university of bristol')
    nb.add('research/edu', 'the university of melbourne')
    nb.add('research/edu', 'the university of british columbia')
    nb.add('media', 'british broadcasting corporation')
    # nb.save_data()
##    nb.load_data()
    print(nb.classify('british broadcasting commission'))
    print(nb.classify('university of florida'))
    print(nb.classify('bristol university'))
    print(nb.classify('australian broadcasting commission'))
    # print(repr(nb.priors))
    # print(repr(nb.total))
    # print(repr(nb.count))
    # print(nb.total.get('media').get('british'))
    # print(nb.total.get('research/edu').get('university'))
