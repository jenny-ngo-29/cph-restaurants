import pandas as pd

# Load the CSV file
# Change the separator if needed, e.g. sep=';' or sep='\t'
df = pd.read_csv('clustered_output.csv')

# Columns to average
columns_to_average = [
    'Average star rating',
    'Review count',
    'mean_compound',
    'pct_positive',
    'pct_negative'
]

# Group by cluster and calculate averages
cluster_averages = (
    df.groupby('cluster')[columns_to_average]
    .mean()
    .reset_index()
)

# Optional: round values for cleaner output
cluster_averages = cluster_averages.round(3)

# Print results
print(cluster_averages)

# Optional: save to a new CSV
cluster_averages.to_csv('cluster_averages.csv', index=False)