import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

df = pd.read_csv("copenhagen_cafes.csv")

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
    "Outdoor seating",
    "Vegan options",
    "Vegetarian options",
    "Gluten-free options"
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
plt.figure()
plt.plot(k_range, inertia, marker='o')
plt.xlabel("k")
plt.ylabel("Inertia")
plt.title("Elbow Method")
plt.show()

optimal_k = 4

kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
df["Cluster"] = kmeans.fit_predict(X_scaled)

df.to_csv("clustered_cafes.csv", index=False)

print("Saved clustered_cafes.csv")