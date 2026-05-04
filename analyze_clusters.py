import pandas as pd
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA

# Load clustered data
df = pd.read_csv("clustered_restaurants.csv")

# Re-create embeddings from Category
model = SentenceTransformer("all-MiniLM-L6-v2")

texts = df["Category"].astype(str).tolist()
embeddings = model.encode(texts, normalize_embeddings=True)

# Reduce embeddings to 2D
pca = PCA(n_components=2, random_state=42)
points_2d = pca.fit_transform(embeddings)

df["x"] = points_2d[:, 0]
df["y"] = points_2d[:, 1]

# Plot clusters
plt.figure(figsize=(10, 7))

scatter = plt.scatter(
    df["x"],
    df["y"],
    c=df["cluster"],
    alpha=0.7
)

plt.xlabel("PCA 1")
plt.ylabel("PCA 2")
plt.title("Restaurant Category Clusters")
plt.colorbar(scatter, label="Cluster")

plt.show()