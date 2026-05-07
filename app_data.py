import pandas as pd

# Load files
places = pd.read_csv("copenhagen_places_merged.csv")
clusters = pd.read_csv("clustered_output.csv")

# Merge using Yelp ID
df = places.merge(
    clusters[["Yelp ID", "cluster"]],
    on="Yelp ID",
    how="left"
)

# Create Business Type from Category
def classify_business_type(category):
    category = str(category).lower()

    cafe_keywords = [
        "cafe",
        "coffee",
        "bakery",
        "bakeries"
    ]

    if any(keyword in category for keyword in cafe_keywords):
        return "Cafe"

    return "Restaurant"

df["Business Type"] = df["Category"].apply(classify_business_type)

# Remove cluster 4
df = df[df["cluster"] != 4]

# Save combined file
df.to_csv("copenhagen_places_with_clusters.csv", index=False)

print("Saved: copenhagen_places_with_clusters.csv")
print(df["Business Type"].value_counts())
print(df["cluster"].value_counts().sort_index())