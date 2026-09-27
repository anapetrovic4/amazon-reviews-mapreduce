from mrjob.job import MRJob
from mrjob.step import MRStep
import ast

class TopTerms(MRJob):
    def configure_args(self):
        super().configure_args()
        # Allows us to set how many top tokens per category we want (default 75)
        self.add_passthru_arg('--top-n', type=int, default=75)
    
    def steps(self):
        # This job has one step: map and then reduce
        return [MRStep(mapper=self.mapper, reducer=self.reducer)]
    
    def mapper(self, _, line):
        # Each line is a (category, token) pair and its chi-square score
        key, value = line.strip().split('\t')
        category, token = ast.literal_eval(key)
        # Emit category as key, and (token, score) as value
        yield category, (token, float(value))
    
    def reducer(self, category, token_scores):
        # For each category, sort tokens by score (descending) and take top N
        top_n = sorted(token_scores, key=lambda x: -x[1])[:self.options.top_n]
        for token, score in top_n:
            yield category, (token, score)

if __name__ == '__main__':
    TopTerms.run()