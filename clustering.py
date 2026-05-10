import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

import hdbscan

class ClusterModel:
    def __init__(self, min_cluster_size=15):
        self.model = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size)

    def fit(self, X):
        return self.model.fit_predict(X)
    
    
df = pd.read_csv("copenhagen_places_merged.csv", on_bad_lines="skip")
def price_to_num(price):
    if isinstance(price, str):
        return len(price)
    return 0

df["Price"] = df["Price"].apply(price_to_num)

# Convert booleans (True/False) → 1/0
bool_cols = [
    "Outdoor seating",
    "Vegan options",
    "Vegetarian options",
    "Gluten-free options"
]

for col in bool_cols:
    df[col] = df[col].astype(int)

# Fill missing values
df = df.fillna(0)

features = [
    "Average star rating",
    "Review count",
    "Price",
    # "Outdoor seating",
    # "Vegan options",
    # "Vegetarian options",
    # "Gluten-free options"
]

X = df[features]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

inertia = []
k_range = range(1, 11)

for k in k_range:
    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    model.fit(X_scaled)
    inertia.append(model.inertia_)

# Plot elbow
# plt.figure()
# plt.plot(k_range, inertia, marker='o')
# plt.xlabel("k")
# plt.ylabel("Inertia")
# plt.title("Elbow Method")
# plt.show()

# optimal_k = 4

# kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
# df["Cluster"] = kmeans.fit_predict(X_scaled)

# df.to_csv("clustered_restaurants.csv", index=False)

# print("Saved clustered_restaurants.csv")

# pca = PCA(n_components=2)
# X_pca = pca.fit_transform(X_scaled)

# plt.figure()

# for cluster in set(df["Cluster"]):
#     subset = X_pca[df["Cluster"] == cluster]
#     plt.scatter(subset[:, 0], subset[:, 1], label=f"Cluster {cluster}")

# plt.xlabel("PCA 1")
# plt.ylabel("PCA 2")
# plt.title("Restaurant Clusters Visualization")
# plt.legend()
# plt.show()