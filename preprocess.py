from mrjob.job import MRJob
import json
import re

class Preprocess(MRJob):
    def configure_args(self):
        super().configure_args()
        # Allows us to specify a stopwords file from the command line
        self.add_file_arg('--stopwords-file')
        
    def mapper_init(self):
        # This runs once per mapper process.
        # Here we load all stopwords into a set for fast lookup.
        with open(self.options.stopwords_file) as f:
            self.stopwords = set(line.strip() for line in f)
        # Define delimiters for splitting text into tokens (words)
        self.delimiters = r"[ \t\d\(\)\[\]\{\}\.\!\?\,;:\+=\-_\"'`~#@&\*%€$§\\\/]+"
    
    def mapper(self, _, line):
        try:
            # Parse each input line as JSON (one review per line)
            review = json.loads(line)
            # Convert review text to lowercase for normalization
            text = review['reviewText'].lower()
            # Split text into tokens using the defined delimiters
            tokens = re.split(self.delimiters, text)
            # Remove stopwords and single-character tokens
            filtered = [t for t in tokens if len(t) > 1 and t not in self.stopwords]
            
            # Prepare the result as a dictionary with category and filtered text
            result = {
                "reviewCategory": review['category'],
                "filteredReviewText": " ".join(filtered)
            }
            # Output the result as a JSON line (one per review)
            print(json.dumps(result))
        except Exception as e:
            # If something goes wrong, increment an error counter (for debugging)
            self.increment_counter('errors', 'preprocessing_error', 1)

if __name__ == '__main__':
    Preprocess.run()