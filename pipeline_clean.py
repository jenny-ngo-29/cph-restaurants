"""
Restaurant Clustering Pipeline
--------------------------------
Features:
  - Raw numeric      : Star rating, Review count, Price
  - Sentiment        : mean_compound, pct_positive, pct_negative (pre-computed)
  - Text embeddings  : Category, Ambience, Review Highlights, Customer Experience

Each group has its own weight so you can tune their influence independently.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer

# ── Config ────────────────────────────────────────────────────────────────────
INPUT_FILE   = "final_clustered_restaurants.csv"
OUTPUT_FILE  = "clustered_output.csv"
N_CLUSTERS   = 7
TFIDF_DIMS   = 100    # TF-IDF dims reduced via SVD (LSA)

# Tune each group's influence on clustering independently
WEIGHT_NUMERIC    = 5.0   # star rating, review count, price
WEIGHT_SENTIMENT  = 0.5   # mean_compound, pct_positive, pct_negative
WEIGHT_EMBEDDINGS = 0.4   # semantic text (category, ambience, highlights, etc.)


# ── 1. Load ───────────────────────────────────────────────────────────────────
df = pd.read_csv(INPUT_FILE)
print(f"Loaded {len(df)} restaurants")


# ── 2. Raw numeric features (price, rating, volume) ──────────────────────────
def price_to_int(p):
    """'$$' → 2,  '$$$' → 3, etc."""
    return len(p) if isinstance(p, str) else np.nan

df["price_num"] = df["Price"].apply(price_to_int)

raw_numeric_cols = [
    "Average star rating",
    "Review count",
    "price_num",
]

raw_df = df[raw_numeric_cols].copy().fillna(df[raw_numeric_cols].median())
raw_scaled = StandardScaler().fit_transform(raw_df)


# ── 3. Sentiment features ─────────────────────────────────────────────────────
sentiment_cols = [
    "mean_compound",   # overall polarity (-1 → +1)
    "pct_positive",    # % positive reviews
    "pct_negative",    # % negative reviews
]

sentiment_df = df[sentiment_cols].copy().fillna(df[sentiment_cols].median())
sentiment_scaled = StandardScaler().fit_transform(sentiment_df)


# ── 4. Text embeddings (semantic richness) ────────────────────────────────────
text_series = (
    df["Category"].fillna("") + " | " +
    df["Ambience"].fillna("") + " | " +
    df["Review Highlights"].fillna("") + " | " +
    df["Customer Experience"].fillna("")
)

print("Building TF-IDF text embeddings (LSA)…")
tfidf = TfidfVectorizer(max_features=5000, sublinear_tf=True, ngram_range=(1, 2))
tfidf_matrix = tfidf.fit_transform(text_series.tolist())

svd = TruncatedSVD(n_components=TFIDF_DIMS, random_state=42)
embeddings = svd.fit_transform(tfidf_matrix)

# L2-normalise so cosine similarity is preserved
norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
embeddings = embeddings / np.where(norms == 0, 1, norms)
print(f"Embeddings shape: {embeddings.shape}")


# ── 5. Combine all feature groups with independent weights ────────────────────
X = np.hstack([
    raw_scaled        * WEIGHT_NUMERIC,
    sentiment_scaled  * WEIGHT_SENTIMENT,
    embeddings        * WEIGHT_EMBEDDINGS,
])


# ── 6. Elbow method (runs if N_CLUSTERS is None, skips if already set) ────────
if N_CLUSTERS is None:
    print("\nRunning elbow method to find optimal k…")
    K_RANGE = range(2, 12)
    inertias = []
    for k in K_RANGE:
        km = KMeans(n_clusters=k, random_state=42, n_init="auto")
        km.fit(X)
        inertias.append(km.inertia_)
        print(f"  k={k}  inertia={km.inertia_:.1f}")

    fig_e, ax_e = plt.subplots(figsize=(8, 5))
    ax_e.plot(list(K_RANGE), inertias, "o-", color="steelblue", linewidth=2, markersize=7)
    ax_e.set_xlabel("Number of clusters (k)", fontsize=12)
    ax_e.set_ylabel("Inertia", fontsize=12)
    ax_e.set_title("Elbow Method — pick k at the bend", fontsize=13, fontweight="bold")
    ax_e.set_xticks(list(K_RANGE))
    ax_e.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("elbow_plot.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Elbow plot saved → elbow_plot.png")

    N_CLUSTERS = int(input("\nEnter k to use for clustering: ").strip())


# ── 7. Cluster ────────────────────────────────────────────────────────────────
kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init="auto")
df["cluster"] = kmeans.fit_predict(X)
print(f"\nCluster sizes:\n{df['cluster'].value_counts().sort_index()}")


# ── 8. Build cluster labels from top categories ───────────────────────────────
def top_categories(group, n=3):
    cats = group["Category"].dropna().str.split(r"[,/]").explode().str.strip()
    return " / ".join(cats.value_counts().head(n).index.tolist())

cluster_labels = {
    cid: f"Cluster {cid}: {top_categories(grp)}"
    for cid, grp in df.groupby("cluster")
}
print("\nCluster descriptions:")
for cid, label in cluster_labels.items():
    print(f"  {label}")


# ── 9. Visualise ──────────────────────────────────────────────────────────────
pca = PCA(n_components=2, random_state=42)
pts = pca.fit_transform(X)
variance = pca.explained_variance_ratio_ * 100

COLORS = plt.cm.tab10.colors
fig, ax = plt.subplots(figsize=(11, 8))

for cid in sorted(df["cluster"].unique()):
    mask = df["cluster"] == cid
    ax.scatter(
        pts[mask, 0], pts[mask, 1],
        c=[COLORS[cid % len(COLORS)]],
        alpha=0.75, s=60,
        edgecolors="white", linewidths=0.4,
        label=cluster_labels[cid],
    )

for cid in sorted(df["cluster"].unique()):
    mask = df["cluster"] == cid
    cx, cy = pts[mask, 0].mean(), pts[mask, 1].mean()
    ax.scatter(cx, cy, c=[COLORS[cid % len(COLORS)]], s=200,
               marker="*", edgecolors="black", linewidths=0.8, zorder=5)
    ax.annotate(str(cid), (cx, cy), fontsize=9, fontweight="bold",
                ha="center", va="bottom", xytext=(0, 8), textcoords="offset points")

ax.set_xlabel(f"PC 1 ({variance[0]:.1f}% variance)", fontsize=11)
ax.set_ylabel(f"PC 2 ({variance[1]:.1f}% variance)", fontsize=11)
ax.set_title("Restaurant Clusters\n(Sentiment + Text Embeddings + Price / Rating / Volume)",
             fontsize=13, fontweight="bold")
ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=8, frameon=True, title="Clusters")

plt.tight_layout()
plt.savefig("cluster_plot.png", dpi=150, bbox_inches="tight")
print("\nPlot saved → cluster_plot.png")


# ── 10. Save ──────────────────────────────────────────────────────────────────
keep_cols = [
    "Yelp ID", "Business name", "Category", "Average star rating",
    "Review count", "Price", "Ambience",
    "mean_compound", "pct_positive", "pct_negative", "cluster",
]
df[keep_cols].to_csv(OUTPUT_FILE, index=False)
print(f"Results saved → {OUTPUT_FILE}")