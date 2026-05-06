import pandas as pd

# def merge_and_dedupe(file1, file2, output_file):
#     # Load both CSVs
#     df1 = pd.read_csv(file1)
#     df2 = pd.read_csv(file2)

#     # Combine
#     combined = pd.concat([df1, df2], ignore_index=True)

#     # Drop duplicates based on Yelp ID (keep first occurrence)
#     deduped = combined.drop_duplicates(subset="Yelp ID", keep="first")

#     # Save
#     deduped.to_csv(output_file, index=False)

#     print(f"Merged file saved to {output_file}")
#     print(f"Original rows: {len(df1) + len(df2)}")
#     print(f"After deduplication: {len(deduped)}")

# if __name__ == "__main__":
#     merge_and_dedupe(
#         "copenhagen_restaurants_merged.csv",
#         "copenhagen_cafes.csv",
#         "copenhagen_places_merged.csv"
#     )

df_main = pd.read_csv("copenhagen_places_merged.csv")
df_sent = pd.read_csv("business_sentiment_summary.csv")

df = df_main.merge(df_sent, on="Yelp ID", how="left")