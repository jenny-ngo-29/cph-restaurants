import pandas as pd

# Load the file
df = pd.read_csv('clustered_output.csv')

# Convert Price ($, $$, $$$, $$$$) into numeric values
# Example: '$$$' -> 3
df['Price_Numeric'] = df['Price'].astype(str).str.count(r'\$')

# Columns to average
columns_to_average = [
    'Average star rating',
    'Review count',
    'mean_compound',
    'pct_positive',
    'pct_negative',
    'Price_Numeric'
]

# Group by cluster and calculate averages
cluster_averages = (
    df.groupby('cluster')[columns_to_average]
    .mean()
    .reset_index()
)

# Optional rounding
cluster_averages = cluster_averages.round(3)

# Rename for readability
cluster_averages = cluster_averages.rename(
    columns={'Price_Numeric': 'Average_Price_Level'}
)

# Print results
print(cluster_averages)

# Save to CSV
cluster_averages.to_csv('cluster_averages.csv', index=False)