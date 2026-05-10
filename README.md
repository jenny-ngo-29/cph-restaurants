# cph-restaurants

To obtain data, set YELP_API_KEY as a .env and run restaurants.py. This outputs 2 csv files, copenhagen_restaurants.csv and copenhagen_cafes.csv. Current data has merged these 2 files into copenhagen_places_merged.csv. 

Run sentiment analysis after data is obtained: python sentiment.py
- This outputs a csv with sentiment analysis for each restaurant with written fields for reviews, highlights, and descriptions. 
- prerequisite: copenhagen_places_merged.csv must exist in directory

Obtain clusters by running pipline.py. Outputs cluster_plot.png and clustered_output.csv. 

clustered_output.csv contains all restaurants with raw data and which cluster they belong to. 

User interface launched using command: streamlit run app.py