import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Copenhagen Food Recommender",
    page_icon="🍽️",
    layout="centered"
)

st.markdown(
    """
    <style>

    .stApp {
        background-color: #f4efe6;
    }

    h1, .main-title {
        color: #0b1f3a !important;
        text-align: center;
        font-size: 52px;
        font-weight: 800;
        margin-bottom: 10px;
    }

    h2, h3 {
        color: #0b1f3a !important;
    }

    .subtitle {
        text-align: center;
        font-size: 20px;
        color: #0b1f3a !important;
        margin-bottom: 35px;
    }

    p {
        color: #0b1f3a !important;
    }

    .stSelectbox label {
        color: #0b1f3a !important;
        font-weight: 600;
    }

    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #102542 !important;
        border-radius: 10px !important;
        border: none !important;
    }

    .stSelectbox div[data-baseweb="select"] span {
        color: white !important;
    }

    .stSelectbox svg {
        fill: white !important;
    }

    details summary {
        background-color: #102542 !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
    }

    details summary p {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 18px !important;
    }

    details summary svg {
        fill: #FFFFFF !important;
    }

    .stButton button {
        background-color: #102542 !important;
        border-radius: 10px;
        border: none;
        font-weight: 600;
    }

    .stButton button p {
        color: white !important;
    }

    .stButton button:hover {
        background-color: #1f3b63 !important;
    }

    .stButton button:hover p {
        color: white !important;
    }

    .stLinkButton a {
        background-color: #102542 !important;
        border-radius: 10px;
        border: none;
        font-weight: 600;
        text-decoration: none;
    }

    .stLinkButton a p {
        color: white !important;
    }

    .stLinkButton a:hover {
        background-color: #1f3b63 !important;
    }

    .stLinkButton a:hover p {
        color: white !important;
    }

    div[class*="st-key-recommendation_card_"] {
        padding: 22px;
        border-radius: 18px;
        background-color: #f9f6f1;
        border: 1px solid #e6ded3;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 24px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

def clean_value(value, fallback="Not available"):
    if pd.isna(value) or str(value).strip().lower() in ["", "nan", "none"]:
        return fallback
    return value

df = pd.read_csv("copenhagen_places_with_clusters.csv")
df = df[df["cluster"] != 4]

st.markdown(
    """
    <h1 class="main-title">🍽️ Copenhagen Food Recommender</h1>
    <p class="subtitle">
        Discover restaurants and cafes based on your preferred vibe
    </p>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <p style="font-size: 18px;">
        Choose what kind of place you want, and we’ll recommend places from your Yelp dataset.
    </p>
    """,
    unsafe_allow_html=True
)

business_type = st.selectbox(
    "Do you want a restaurant, cafe, or both?",
    ["Restaurant", "Cafe", "Both"]
)

if business_type == "Both":
    filtered = df.copy()
else:
    filtered = df[df["Business Type"] == business_type]

cluster_descriptions = {
    0: "Budget Eats",
    1: "Casual Dining",
    2: "Copenhagen Favorites",
    3: "Fine Dining",
    5: "Trendy & Social",
    6: "Hidden Gems"
}

cluster_long_descriptions = {
    0: "Affordable, casual places that are good for quick meals, takeaway, coffee, or low-cost eats.",
    1: "Comfortable mid-range spots for casual sit-down meals, brunch, and everyday dining.",
    2: "Highly popular Copenhagen places with lots of reviews and strong public recognition.",
    3: "Higher-end restaurants with a more upscale or fine-dining feel.",
    5: "Trendy, social, and popular casual spots that work well for groups or relaxed outings.",
    6: "Highly rated places with fewer reviews, making them feel more like hidden gems."
}

cluster_choice = st.selectbox(
    "What kind of place are you in the mood for?",
    list(cluster_descriptions.keys()),
    format_func=lambda x: cluster_descriptions[x]
)

with st.expander("ℹ️ About this cluster"):
    st.write(cluster_long_descriptions[cluster_choice])

filtered = filtered[filtered["cluster"] == cluster_choice]

if st.button("Recommend places", use_container_width=True):

    if filtered.empty:
        st.warning("No matching places found. Try another cluster or type.")

    else:
        num_recommendations = min(10, len(filtered))
        recommendations = filtered.sample(num_recommendations)

        st.markdown("---")
        st.subheader(f"Here are {num_recommendations} recommendations:")

        for i, (_, recommendation) in enumerate(recommendations.iterrows()):

            with st.container(key=f"recommendation_card_{i}"):

                st.markdown(
                    f"""
                    <h2 style="margin-bottom: 4px; color: #0b1f3a !important; font-weight: 700;">
                        {clean_value(recommendation['Business name'])}
                    </h2>

                    <p style="font-size: 16px; color: #555 !important;">
                        {clean_value(recommendation['Category'])}
                    </p>

                    <p style="font-size: 18px; color: #0b1f3a !important;">
                        ⭐ <b>{clean_value(recommendation['Average star rating'])}</b>
                        &nbsp;&nbsp; | &nbsp;&nbsp;
                        📝 {clean_value(recommendation['Review count'])} reviews
                        &nbsp;&nbsp; | &nbsp;&nbsp;
                        💰 {clean_value(recommendation.get('Price'), 'No price data')}
                    </p>
                    """,
                    unsafe_allow_html=True
                )

                yelp_url = recommendation.get("Yelp profile URL")

                if pd.notna(yelp_url) and str(yelp_url).strip() != "":
                    st.link_button(
                        "View on Yelp",
                        yelp_url,
                        use_container_width=True
                    )

                with st.expander("📍 Business Information"):
                    st.markdown(f"**Address:** {clean_value(recommendation.get('Business address'))}")
                    st.markdown(f"**Phone number:** {clean_value(recommendation.get('Phone number'))}")

                    business_url = recommendation.get("Business website URL")

                    if pd.notna(business_url) and str(business_url).strip() != "":
                        st.markdown(f"**Business URL:** {business_url}")
                    else:
                        st.markdown("**Business URL:** Not available")

                with st.expander("💬 Review Highlights"):
                    review_highlights = recommendation.get("Review Highlights")

                    if pd.notna(review_highlights) and str(review_highlights).strip() != "":
                        st.write(review_highlights)
                    else:
                        st.write("No review highlights available.")