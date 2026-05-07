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

    h2 {
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

    /* Dropdown label */
    .stSelectbox label {
        color: #0b1f3a !important;
    }
    
    /* Dropdown labels */
    .stSelectbox label {
        color: #0b1f3a !important;
        font-weight: 600;
    }

    /* Recommend button */

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

    /* Yelp button */

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

    </style>
    """,
    unsafe_allow_html=True
)

# Load data
df = pd.read_csv("copenhagen_places_with_clusters.csv")

# Remove missing-data cluster
df = df[df["cluster"] != 4]

# Title section
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
        Choose what kind of place you want, and we’ll recommend one from your Yelp dataset.
    </p>
    """,
    unsafe_allow_html=True
)

# Business type selector
business_type = st.selectbox(
    "Do you want a restaurant or cafe?",
    ["Restaurant", "Cafe"]
)

# Filter by type
filtered = df[df["Category"].str.contains(business_type, case=False, na=False)]

# Cluster labels
cluster_descriptions = {
    0: "Budget Eats",
    1: "Casual Dining",
    2: "Copenhagen Favorites",
    3: "Fine Dining",
    5: "Trendy & Social",
    6: "Hidden Gems"
}

# Cluster selector
cluster_choice = st.selectbox(
    "What kind of place are you in the mood for?",
    list(cluster_descriptions.keys()),
    format_func=lambda x: cluster_descriptions[x]
)

# Filter by cluster
filtered = filtered[filtered["cluster"] == cluster_choice]

# Recommendation button
if st.button("Recommend a place", use_container_width=True):

    if filtered.empty:
        st.warning("No matching places found. Try another cluster or type.")

    else:
        recommendation = filtered.sample(1).iloc[0]

        st.markdown("---")

        # Recommendation card
        # Recommendation card
        st.markdown(
            f"""
            <div style="padding: 24px; border-radius: 18px; background-color: #f9f6f1; border: 1px solid #e6ded3; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                <h2 style="margin-bottom: 4px; color: #0b1f3a !important; font-weight: 700;">
                    {recommendation['Business name']}
                </h2>
                <p style="font-size: 16px; color: #555 !important;">
                    {recommendation['Category']}
                </p>
                <p style="font-size: 18px; color: #0b1f3a !important;">
                    ⭐ <b>{recommendation['Average star rating']}</b>
                    &nbsp;&nbsp; | &nbsp;&nbsp;
                    📝 {recommendation['Review count']} reviews
                    &nbsp;&nbsp; | &nbsp;&nbsp;
                    💰 {recommendation.get('Price', 'No price data')}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")

        # Yelp button
        yelp_url = recommendation.get("Yelp profile URL")

        if pd.notna(yelp_url) and str(yelp_url).strip() != "":
            st.link_button(
                "View on Yelp",
                yelp_url,
                use_container_width=True
            )

        # Business information
        with st.expander("📍 Business information"):

            st.markdown(
                f"**Address:** "
                f"{recommendation.get('Business address', 'Not available')}"
            )

            st.markdown(
                f"**Phone number:** "
                f"{recommendation.get('Phone number', 'Not available')}"
            )

            business_url = recommendation.get("Business website URL")

            if pd.notna(business_url) and str(business_url).strip() != "":
                st.markdown(f"**Business URL:** {business_url}")

            else:
                st.markdown("**Business URL:** Not available")

        # Review highlights
        with st.expander("💬 Review highlights"):

            review_highlights = recommendation.get("Review Highlights")

            if (
                pd.notna(review_highlights)
                and str(review_highlights).strip() != ""
            ):
                st.write(review_highlights)

            else:
                st.write("No review highlights available.")