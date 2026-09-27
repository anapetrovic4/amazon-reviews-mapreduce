
# Finding Category-Specific Terms in Amazon Reviews

**Data Intensive Computing · Assignment 1 · TU Wien**  
**Authors:** Lucija Aleksic, Filip Aleksic, Anabel Dautovic, Ana Petrovic, Maty Prechl  
**Report date:** April 29, 2025


## At a glance

| | |
|---|---|
| **Dataset** | Amazon Review Dataset 2014; 142.8 million reviews across 24 product categories, as described in the report |
| **Stack** | Python, `mrjob`, Hadoop MapReduce, HDFS, shell scripting |
| **Ranking method** | Chi-square association between term presence and product category |
| **Default output** | Top 75 terms per category, with scores, plus a merged vocabulary |
| **Reported runtime** | Approximately 30 minutes on the TU Wien cluster; cluster load may have affected it |

## Pipeline

| Stage | Script | What it does |
|:--:|---|---|
| 1 | `preprocess.py` | Parses JSON reviews, lowercases and tokenizes text, removes stopwords and single-character tokens. |
| 2 | `token_category_counts.py` | Counts documents by category, documents containing each term, and documents containing each category–term pair. |
| 3 | `chi_square.py` | Computes a chi-square score for every category–term pair from the aggregated counts. |
| 4 | `top75_per_category.py` | Ranks terms within each category and retains the top *N* (75 by default). |
| 5 | `generate_output.py` | Formats category-level rankings and builds a merged dictionary of unique terms. |

`src/run_pipeline.sh` runs these jobs in order, manages paths and Hadoop commands, and accepts the requested number of terms as a parameter.

### How the score works

For a given category and term, the pipeline forms a 2 × 2 table of **document counts**:

| | Term appears | Term does not appear |
|---|---:|---:|
| **Review belongs to category** | A | C |
| **Review belongs to another category** | B | D |

$$\chi^2 = \frac{N(AD-BC)^2}{(A+B)(C+D)(A+C)(B+D)}, \qquad N=A+B+C+D$$

A larger score indicates a stronger departure from independence between the term and category. Ranking by this score surfaces distinctive terms; the score alone does not show whether an association is positive or negative.

## Example result

The report shows the following leading terms for `Apps_for_Android`:

| Term | Chi-square score |
|---|---:|
| `games` | 2,537,037.1056 |
| `play` | 2,247,115.1857 |
| `graphics` | 1,713,265 |

The final format lists each category followed by its ranked `term:score` entries. The table is an excerpt from the report, not a complete output file.

## Running on the TU Wien cluster

The commands below reflect the environment and paths documented in the report. Replace `<username>` with your cluster username and adjust paths for your deployment. The review input path is specific to the TU Wien cluster.

```bash
# From your local machine
scp assignment1.zip <username>@lbd.tuwien.ac.at:~
ssh <username>@lbd.tuwien.ac.at
```

```bash
# On the cluster
unzip assignment1.zip
hdfs dfs -mkdir -p input
hdfs dfs -put data/stopwords.txt input/stopwords.txt
chmod +x src/run_pipeline.sh src/*.py

src/run_pipeline.sh \
  hdfs:///user/dic25_shared/amazon-reviews/full/reviewscombined.json \
  hdfs:///user/<username>/input/stopwords.txt \
  output_full \
  75
```

| Argument | Meaning |
|:--:|---|
| 1 | HDFS path to the JSON-lines review dataset |
| 2 | HDFS path to the stopwords file |
| 3 | Output location |
| 4 | Number of top terms per category |

Retrieve the result after the jobs complete:

```bash
# On the cluster
hdfs dfs -get output_full/part-00000 ~/output_full.txt

# From your local machine
scp <username>@lbd.tuwien.ac.at:~/output_full.txt .
```

## Input and output

Each input line is a JSON review containing fields such as `reviewText` and `category`. Preprocessing produces cleaned review text paired with its category. The final output provides ranked terms and scores for each category, as well as a merged dictionary of unique terms.

## Notes

- Counts are based on whether a term occurs in a review, rather than how many times it occurs within that review.
- The reported dataset size and runtime come from the accompanying assignment report; this README does not claim a new benchmark.
- The original report documents the pipeline and sample output, but does not include the complete result set or reproducible local setup instructions.