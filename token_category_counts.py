from mrjob.job import MRJob
import json

class TokenCategoryCounts(MRJob):
    def mapper(self, _, line):
        # For each line (one review), parse the JSON
        data = json.loads(line)
        category = data["reviewCategory"]
        # Split the filtered review text into unique tokens (words)
        tokens = set(data["filteredReviewText"].split())

        # Count one document for this category
        yield ("__CATEGORY_DOC__", category), 1
        # Count one total document
        yield ("__TOTAL_DOCS__", "TOTAL"), 1

        # For each unique token in this review:
        for token in tokens:
            # Count one document for this token (regardless of category)
            yield ("__TOKEN_DOC__", token), 1
            # Count one document for this (category, token) pair
            yield ((category, token), 1)

    def combiner(self, key, values):
        # Locally sum up counts for each key before sending to reducer
        yield key, sum(values)

    def reducer(self, key, values):
        # Globally sum up counts for each key
        yield key, sum(values)

if __name__ == '__main__':
    TokenCategoryCounts.run()