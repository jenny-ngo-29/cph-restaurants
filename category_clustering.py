import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans

# data
df = pd.read_csv("copenhagen_places_merged.csv")

# Keep relevant columns and drop missing values
df = df[["Yelp ID", "Business name", "Category"]].dropna()

# cleaning
df["Category"] = df["Category"].astype(str)
df["Category"] = df["Category"].str.replace("&", "and")
df["Category"] = df["Category"].str.replace(",", " ")

# num clusters
k = 4  # adjust this

# -----------------------------
# 3. Load embedding model
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# 4. Convert text → embeddings
# -----------------------------
texts = df["Category"].tolist()
embeddings = model.encode(texts, normalize_embeddings=True)

# -----------------------------
# 5. Run clustering
# -----------------------------
kmeans = KMeans(n_clusters=k, random_state=42, n_init="auto")
df["cluster"] = kmeans.fit_predict(embeddings)

# -----------------------------
# 6. Save results
# -----------------------------
df.to_csv("clustered_restaurants.csv", index=False)

