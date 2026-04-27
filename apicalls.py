import os
import requests

API_KEY = os.getenv("YELP_API_KEY")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

SEARCH_URL = "https://api.yelp.com/v3/businesses/search"
DETAILS_URL = "https://api.yelp.com/v3/businesses/{}"
REVIEWS_URL = "https://api.yelp.com/v3/businesses/{}/reviews"


def search_restaurants(location="Copenhagen", limit=10):
    params = {
        "location": location,
        "categories": "restaurants",
        "limit": limit
    }
    res = requests.get(SEARCH_URL, headers=HEADERS, params=params)
    return res.json().get("businesses", [])


def get_details(business_id):
    res = requests.get(DETAILS_URL.format(business_id), headers=HEADERS)
    return res.json()


def get_reviews(business_id):
    res = requests.get(REVIEWS_URL.format(business_id), headers=HEADERS)
    return res.json().get("reviews", [])


# --- SIMPLE NLP TAGGING ---
def extract_tags(reviews):
    text = " ".join([r["text"].lower() for r in reviews])

    def has(words):
        return any(w in text for w in words)

    return {
        "ambience": "cozy" if has(["cozy", "romantic"]) else None,
        "noise_level": "loud" if has(["loud", "noisy"]) else "quiet" if has(["quiet"]) else None,
        "outdoor_seating": has(["outdoor", "patio"]),
        "vegan_options": has(["vegan"]),
        "vegetarian_options": has(["vegetarian"]),
        "gluten_free_options": has(["gluten-free"]),
        "alcohol_served": has(["wine", "beer", "cocktail"]),
        "happy_hour": has(["happy hour"]),
        "best_nights": "weekend" if has(["friday", "saturday"]) else None
    }


def build_dataset():
    businesses = search_restaurants()
    dataset = []

    for b in businesses:
        details = get_details(b["id"])
        reviews = get_reviews(b["id"])
        tags = extract_tags(reviews)

        entry = {
            # Core
            "business_name": b["name"],
            "business_address": " ".join(b["location"]["display_address"]),
            "category": [c["title"] for c in b["categories"]],
            "phone_number": b.get("display_phone"),
            "average_star_rating": b["rating"],
            "review_count": b["review_count"],
            "closure_status": b["is_closed"],
            "yelp_profile_url": b["url"],
            "price": b.get("price"),

            # Details
            "hours_of_operation": details.get("hours"),
            "business_website_url": details.get("url"),
            "yelp_menu_url": details.get("menu_url", None),

            # Derived / Missing
            "review_highlights": [r["text"] for r in reviews],
            "business_summary": reviews[0]["text"] if reviews else None,
            "customer_experience": reviews[0]["text"] if reviews else None,

            # NLP-derived tags
            "ambience": tags["ambience"],
            "noise_level": tags["noise_level"],
            "outdoor_seating": tags["outdoor_seating"],
            "vegan_options": tags["vegan_options"],
            "vegetarian_options": tags["vegetarian_options"],
            "gluten_free_options": tags["gluten_free_options"],
            "alcohol_served": tags["alcohol_served"],
            "happy_hour_special": tags["happy_hour"],
            "best_nights": tags["best_nights"],

            # Not available from Yelp API
            "hot_and_new_status": None  # not exposed
        }

        dataset.append(entry)

    return dataset


if __name__ == "__main__":
    data = build_dataset()
    for d in data:
        print(d)
        print("-" * 80)