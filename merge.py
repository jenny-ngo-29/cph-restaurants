import pandas as pd

def aggregate_sentiment(reviews_file):
    #Collapse per-review rows into one row per restaurant.
    df = pd.read_csv(reviews_file)

    numeric_agg = df.groupby("Yelp ID").agg(
        mean_compound          = ("vader_compound", "mean"),
        mean_pos               = ("vader_pos",      "mean"),
        mean_neg               = ("vader_neg",      "mean"),
        mean_neu               = ("vader_neu",      "mean"),
        review_count_sentiment = ("vader_compound", "count"),
    )

    label_counts = df.groupby(["Yelp ID", "vader_label"]).size().unstack(fill_value=0)
    label_pct = label_counts.div(label_counts.sum(axis=1), axis=0) * 100
    label_pct = label_pct.rename(columns={
        "positive": "pct_positive",
        "negative": "pct_negative",
        "neutral":  "pct_neutral",
    })
    for col in ["pct_positive", "pct_negative", "pct_neutral"]:
        if col not in label_pct.columns:
            label_pct[col] = 0.0

    return numeric_agg.join(label_pct[["pct_positive", "pct_negative", "pct_neutral"]]).reset_index()


def merge_and_save(places_file, reviews_file, summary_file, output_file):
    df_places  = pd.read_csv(places_file)

    # Aggregate raw reviews into one row per restaurant
    df_reviews = aggregate_sentiment(reviews_file)

    # Pull only the extra columns from the summary that reviews don't have
    df_summary = pd.read_csv(summary_file)[["Yelp ID", "weighted_compound", "review_snippets"]]

    # merge places and reviews and summary
    df = df_places.merge(df_reviews, on="Yelp ID", how="left")
    df = df.merge(df_summary, on="Yelp ID", how="left")

    df.to_csv(output_file, index=False)

    print(f"Saved → {output_file}")
    print(f"Total places         : {len(df)}")
    print(f"With review sentiment: {df['mean_compound'].notna().sum()}")
    print(f"With weighted_compound: {df['weighted_compound'].notna().sum()}")
    print(f"No sentiment at all  : {df['mean_compound'].isna().sum()}")


if __name__ == "__main__":
    merge_and_save(
        places_file  = "copenhagen_places_merged.csv",
        reviews_file = "reviews_sentiment.csv",
        summary_file = "business_sentiment_summary.csv",
        output_file  = "final_clustered_restaurants.csv",
    )