#!/bin/bash

# Read input arguments: input file, stopwords file, output folder, and number of top terms (default 75)
INPUT=$1
STOPWORDS=$2
OUTPUT=$3
TOP_N=${4:-75}
STREAMING_JAR=/usr/lib/hadoop/tools/lib/hadoop-streaming-3.3.6.jar

# Clean up any previous outputs from HDFS so the pipeline starts fresh
hdfs dfs -rm -r /user/e12450757/preprocessed 2>/dev/null
hdfs dfs -rm -r /user/e12450757/counts 2>/dev/null
hdfs dfs -rm -r /user/e12450757/chi2 2>/dev/null
hdfs dfs -rm -r /user/e12450757/top_terms 2>/dev/null
hdfs dfs -rm -r $OUTPUT 2>/dev/null

# Step 0: Preprocessing
echo "Step 0: Preprocessing"
# Runs the preprocessing script on Hadoop, which cleans and tokenizes the reviews,
# removes stopwords, and outputs one JSON per review with category and filtered text.
python preprocess.py -r hadoop $INPUT \
    --stopwords-file $STOPWORDS \
    --output-dir hdfs:///user/e12450757/preprocessed \
    --hadoop-streaming-jar $STREAMING_JAR

# Step 1: Token Counts
echo "Step 1: Counting tokens and categories"
# Counts how many documents each category, each token, and each (category, token) pair appears in.
# This prepares the statistics needed for chi-square calculation.
python token_category_counts.py -r hadoop \
    hdfs:///user/e12450757/preprocessed/part* \
    --output-dir hdfs:///user/e12450757/counts \
    --hadoop-streaming-jar $STREAMING_JAR

# Step 2: Chi-Square
echo "Step 2: Calculating Chi-Square values"
# Calculates the chi-square statistic for each (category, token) pair,
# which measures how characteristic a word is for a category.
python chi_square.py -r hadoop \
    hdfs:///user/e12450757/counts/part-00000 \
    --counts hdfs:///user/e12450757/counts/part-00000 \
    --output-dir hdfs:///user/e12450757/chi2 \
    --hadoop-streaming-jar $STREAMING_JAR

# Step 3: Top Terms
echo "Step 3: Selecting top $TOP_N terms per category"
# For each category, selects the top N tokens with the highest chi-square scores.
python top75_per_category.py -r hadoop \
    hdfs:///user/e12450757/chi2/part* \
    --top-n $TOP_N \
    --output-dir hdfs:///user/e12450757/top_terms \
    --hadoop-streaming-jar $STREAMING_JAR

# Step 4: Final Output
echo "Step 4: Generating final output"
# Formats the top tokens for each category into the final output file, ready for analysis or submission.
python generate_output.py -r hadoop \
    hdfs:///user/e12450757/top_terms/part* \
    --output-dir $OUTPUT \
    --hadoop-streaming-jar $STREAMING_JAR

echo "Pipeline completed. Results saved to $OUTPUT"