from mrjob.job import MRJob
import ast
from collections import defaultdict

class ComputeChiSquare(MRJob):
    def configure_args(self):
        super().configure_args()
        # This allows us to pass an extra file (--counts) with global counts needed for chi-square
        self.add_file_arg('--counts')
    
    def mapper_init(self):
        # Here we load all the necessary counts from the counts file:
        # - category_counts: number of documents per category
        # - token_counts: number of documents each token appears in
        # - total_docs: total number of documents
        self.category_counts = defaultdict(int)
        self.token_counts = defaultdict(int)
        self.total_docs = 0
        
        with open(self.options.counts) as f:
            for line in f:
                key, value = line.strip().split('\t')
                key = ast.literal_eval(key)
                if key[0] == '__CATEGORY_DOC__':
                    self.category_counts[key[1]] = int(value)
                elif key[0] == '__TOKEN_DOC__':
                    self.token_counts[key[1]] = int(value)
                elif key[0] == '__TOTAL_DOCS__':
                    self.total_docs = int(value)
    
    def mapper(self, _, line):
        # Each line is a (category, token) pair with its count
        key, value = line.strip().split('\t')
        category, token = ast.literal_eval(key)
        A = int(value)  # Number of documents where this token appears in this category
        
        # B: documents where token appears, but not in this category
        B = self.token_counts.get(token, 0) - A
        # C: documents in this category where token does NOT appear
        C = self.category_counts.get(category, 0) - A
        # D: documents where token does NOT appear and are NOT in this category
        D = self.total_docs - A - B - C
        
        # Calculate chi-square value for this (category, token) pair
        numerator = (A * D - B * C) ** 2
        denominator = (A + B) * (C + D) * (A + C) * (B + D)
        chi2 = (self.total_docs * numerator / denominator) if denominator != 0 else 0
        
        # Emit the result: for each (category, token) pair, its chi-square value
        yield (category, token), chi2

if __name__ == '__main__':
    ComputeChiSquare.run()