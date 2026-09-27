from mrjob.job import MRJob
from collections import defaultdict

class GenerateOutput(MRJob):
    def mapper(self, _, line):
        # Each line contains a category and a (token, score) tuple
        category, value = line.strip().split('\t')
        token, score = eval(value)  # Convert string tuple to Python tuple
        # Emit everything with the same key (None) so all goes to one reducer
        yield None, (category, (token, float(score)))
    
    def reducer(self, _, values):
        # We'll collect all tokens for each category, and also all unique tokens
        category_terms = defaultdict(list)
        all_terms = set()
        
        for category, (token, score) in values:
            category_terms[category].append((token, score))
            all_terms.add(token)
        
        # For each category, sort tokens by score and format as required
        for category in sorted(category_terms.keys()):
            terms = sorted(category_terms[category], key=lambda x: -x[1])
            formatted = ' '.join(f"{t}:{s:.4f}" for t, s in terms)
            yield category, formatted
        
        # Also output a merged dictionary of all unique tokens (optional)
        yield "MERGED_DICT", ' '.join(sorted(all_terms))

if __name__ == '__main__':
    GenerateOutput.run()