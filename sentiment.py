"""
Sentiment Analysis on Copenhagen Yelp Reviews
==============================================
Workflow:
  1. Load CSV (cafes or restaurants)
  2. Parse & clean review text from 'Review Highlights'
  3. Score each review with VADER (fast, lexicon-based, no GPU needed)
  4. Optionally score with a transformer model (better accuracy)
  5. Aggregate per-business and export results
  6. Visualize sentiment distributions

Install dependencies:
    pip install pandas vaderSentiment transformers torch tqdm matplotlib seaborn
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ── Config ──────────────────────────────────────────────────────────────────
CSV_FILE       = "copenhagen_cafes.csv"   # swap for copenhagen_restaurants.csv
OUTPUT_REVIEWS = "reviews_sentiment.csv"
OUTPUT_SUMMARY = "business_sentiment_summary.csv"
USE_TRANSFORMER = False  # set True for higher-accuracy transformer scoring
# ────────────────────────────────────────────────────────────────────────────


# ── 1. Load & parse reviews ──────────────────────────────────────────────────
def load_reviews(filepath: str) -> pd.DataFrame:
    """
    Explode pipe-separated 'Review Highlights' into one row per review,
    keeping business metadata alongside each review snippet.
    """
    df = pd.read_csv(filepath, on_bad_lines="skip")

    # Drop rows with no review text
    df = df[df["Review Highlights"].notna() & (df["Review Highlights"].str.strip() != "")]

    # Split pipe-separated review snippets into individual rows
    df["review_list"] = df["Review Highlights"].str.split(r"\s*\|\s*")
    df_exploded = df.explode("review_list").rename(columns={"review_list": "review_text"})
    df_exploded["review_text"] = df_exploded["review_text"].str.strip()

    # Drop empty snippets that appear after splitting
    df_exploded = df_exploded[df_exploded["review_text"].str.len() > 10].reset_index(drop=True)

    keep_cols = [
        "Yelp ID", "Business name", "Business address", "Category",
        "Average star rating", "Review count", "Price", "review_text"
    ]
    return df_exploded[[c for c in keep_cols if c in df_exploded.columns]]


# ── 2. VADER sentiment scoring ───────────────────────────────────────────────
def score_vader(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds columns: vader_neg, vader_neu, vader_pos, vader_compound, vader_label
    compound: -1 (most negative) → +1 (most positive)
    """
    analyzer = SentimentIntensityAnalyzer()

    scores = df["review_text"].apply(lambda t: analyzer.polarity_scores(str(t)))
    df["vader_neg"]      = scores.apply(lambda s: s["neg"])
    df["vader_neu"]      = scores.apply(lambda s: s["neu"])
    df["vader_pos"]      = scores.apply(lambda s: s["pos"])
    df["vader_compound"] = scores.apply(lambda s: s["compound"])

    def label(c):
        if c >= 0.05:  return "positive"
        if c <= -0.05: return "negative"
        return "neutral"

    df["vader_label"] = df["vader_compound"].apply(label)
    return df


# ── 3. (Optional) Transformer scoring ────────────────────────────────────────
def score_transformer(df: pd.DataFrame, batch_size: int = 32) -> pd.DataFrame:
    """
    Uses distilbert-base-uncased-finetuned-sst-2-english for binary
    positive/negative scoring. Downloads ~260 MB on first run.
    Adds columns: transformer_label, transformer_score
    """
    from transformers import pipeline

    pipe = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        truncation=True,
        max_length=512
    )

    texts  = df["review_text"].tolist()
    labels, scores = [], []

    for i in tqdm(range(0, len(texts), batch_size), desc="Transformer scoring"):
        batch = texts[i : i + batch_size]
        results = pipe(batch)
        for r in results:
            labels.append(r["label"].lower())
            scores.append(round(r["score"], 4))

    df["transformer_label"] = labels
    df["transformer_score"] = scores
    return df


# ── 4. Aggregate per business ────────────────────────────────────────────────
def summarise_by_business(df: pd.DataFrame) -> pd.DataFrame:
    """
    Roll up review-level scores to a per-business summary.
    """
    agg = df.groupby(["Yelp ID", "Business name", "Average star rating", "Price"]).agg(
        review_snippets   = ("review_text",     "count"),
        mean_compound     = ("vader_compound",  "mean"),
        pct_positive      = ("vader_label",     lambda x: (x == "positive").mean()),
        pct_neutral       = ("vader_label",     lambda x: (x == "neutral").mean()),
        pct_negative      = ("vader_label",     lambda x: (x == "negative").mean()),
    ).reset_index()

    agg["mean_compound"]  = agg["mean_compound"].round(3)
    agg["pct_positive"]   = (agg["pct_positive"]  * 100).round(1)
    agg["pct_neutral"]    = (agg["pct_neutral"]   * 100).round(1)
    agg["pct_negative"]   = (agg["pct_negative"]  * 100).round(1)

    agg = agg.sort_values("mean_compound", ascending=False)
    return agg


# ── 5. Visualisations ────────────────────────────────────────────────────────
def plot_sentiment_distribution(df: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Compound score histogram
    axes[0].hist(df["vader_compound"], bins=40, color="steelblue", edgecolor="white")
    axes[0].axvline(0, color="red", linestyle="--", linewidth=1)
    axes[0].set_title("Distribution of VADER Compound Scores")
    axes[0].set_xlabel("Compound score  (−1 negative → +1 positive)")
    axes[0].set_ylabel("Review count")

    # Label proportions
    label_counts = df["vader_label"].value_counts()
    colors = {"positive": "#4caf50", "neutral": "#ff9800", "negative": "#f44336"}
    axes[1].bar(
        label_counts.index,
        label_counts.values,
        color=[colors.get(l, "grey") for l in label_counts.index]
    )
    axes[1].set_title("Sentiment Label Counts")
    axes[1].set_ylabel("Review snippet count")

    plt.tight_layout()
    plt.savefig("sentiment_distribution.png", dpi=150)
    plt.show()
    print("Saved → sentiment_distribution.png")


def plot_top_bottom_businesses(summary: pd.DataFrame, n: int = 15):
    top    = summary.head(n)
    bottom = summary.tail(n).iloc[::-1]
    combined = pd.concat([top, bottom])

    fig, ax = plt.subplots(figsize=(10, 8))
    colors = ["#4caf50" if v >= 0 else "#f44336" for v in combined["mean_compound"]]
    ax.barh(combined["Business name"], combined["mean_compound"], color=colors)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Mean VADER Compound Score")
    ax.set_title(f"Top {n} vs Bottom {n} Businesses by Sentiment")
    plt.tight_layout()
    plt.savefig("top_bottom_sentiment.png", dpi=150)
    plt.show()
    print("Saved → top_bottom_sentiment.png")


def plot_sentiment_vs_stars(summary: pd.DataFrame):
    plt.figure(figsize=(7, 5))
    sns.scatterplot(
        data=summary,
        x="Average star rating",
        y="mean_compound",
        size="review_snippets",
        hue="pct_negative",
        palette="RdYlGn_r",
        sizes=(30, 300),
        alpha=0.75
    )
    plt.title("Sentiment Score vs Star Rating")
    plt.xlabel("Avg Yelp Star Rating")
    plt.ylabel("Mean VADER Compound Score")
    plt.tight_layout()
    plt.savefig("sentiment_vs_stars.png", dpi=150)
    plt.show()
    print("Saved → sentiment_vs_stars.png")


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Loading reviews...")
    reviews = load_reviews(CSV_FILE)
    print(f"  {len(reviews):,} review snippets from {reviews['Business name'].nunique()} businesses")

    print("\nScoring with VADER...")
    reviews = score_vader(reviews)

    if USE_TRANSFORMER:
        print("\nScoring with transformer model...")
        reviews = score_transformer(reviews)

    reviews.to_csv(OUTPUT_REVIEWS, index=False)
    print(f"\nSaved review-level results → {OUTPUT_REVIEWS}")

    print("\nAggregating per business...")
    summary = summarise_by_business(reviews)
    summary.to_csv(OUTPUT_SUMMARY, index=False)
    print(f"Saved business summary → {OUTPUT_SUMMARY}")

    print("\nTop 10 businesses by sentiment:")
    print(summary[["Business name", "mean_compound", "pct_positive", "Average star rating"]].head(10).to_string(index=False))

    print("\nGenerating plots...")
    plot_sentiment_distribution(reviews)
    plot_top_bottom_businesses(summary)
    plot_sentiment_vs_stars(summary)

    print("\nDone.")