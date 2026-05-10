"""
This file preprocesses numerical and categorical features, scales the data, 
and applies PCA to project the multidimensional dataset into two principal components. 
It also uses K-Means to identify four distinct restaurant clusters and visualizes the results 
on a 2D scatter plot labeled with business names.
"""

import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

def main():
    # retrieving restaurant data
    df_restaurants = pd.read_csv("copenhagen_places_merged.csv")

    # getting features for PCA
    pca_features = ['Average star rating', 'Review count']
    df_pca = df_restaurants[pca_features].copy()

    # convert price levels into numbers
    prices = {
        '$': 1,
        '$$': 2,
        '$$$': 3,
        '$$$$': 4
    }

    df_restaurants['Price_num'] = df_restaurants['Price'].map(prices)
    df_pca['Price_num'] = df_restaurants['Price_num']

    # bools into integers
    binary_features = [
        'Outdoor seating',
        'Vegan options',
        'Vegetarian options',
        'Gluten-free options'
    ]

    for feature in binary_features:
        df_pca[feature] = df_restaurants[feature].astype(int)

    # missing values
    df_pca = df_pca.fillna(0)

    # scaling the data
    scaler = StandardScaler()
    df_pca_scaled = scaler.fit_transform(df_pca)

    # applying PCA
    pca = PCA(n_components=2)
    pca_components = pca.fit_transform(df_pca_scaled)

    # PCA columns
    df_pca['PC1'] = pca_components[:, 0]
    df_pca['PC2'] = pca_components[:, 1]

    # KMeans clustering
    kmeans_model = KMeans(
        n_clusters=4,
        random_state=42
    )

    cluster_labels = kmeans_model.fit_predict(df_pca_scaled)


    # adding cluster labels
    df_pca['cluster'] = cluster_labels


    # PCA cluster visualization
    plt.figure(figsize=(10, 7))

    plt.scatter(
        df_pca['PC1'],
        df_pca['PC2'],
        c=df_pca['cluster']
    )

    plt.xlabel("PCA 1")
    plt.ylabel("PCA 2")
    plt.title("Restaurant Clustering w/ PCA")

    for i, name in enumerate(df_restaurants['Business name']):
        plt.text(
            df_pca['PC1'][i],
            df_pca['PC2'][i],
            name,
            fontsize=7
        )

    plt.show()

main()