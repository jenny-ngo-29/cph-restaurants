import os
import requests
import csv
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YELP_API_KEY")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

SEARCH_URL = "https://api.yelp.com/v3/businesses/search"
DETAILS_URL = "https://api.yelp.com/v3/businesses/{}"
REVIEWS_URL = "https://api.yelp.com/v3/businesses/{}/reviews"


# ---- API CALLS ----
def search_restaurants(location="Copenhagen", limit=20):
    params = {
        "location": location,
        "categories": "restaurants",
        "limit": limit
    }
    res = requests.get(SEARCH_URL, headers=HEADERS, params=params)
    return res.json().get("businesses", [])


def get_details(business_id):
    return requests.get(DETAILS_URL.format(business_id), headers=HEADERS).json()


def get_reviews(business_id):
    return requests.get(REVIEWS_URL.format(business_id), headers=HEADERS).json().get("reviews", [])


# ---- SIMPLE NLP TAGGING ----
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
        "happy_hour_special": has(["happy hour"]),
        "best_nights": "weekend" if has(["friday", "saturday"]) else None
    }


# ---- MAIN ----
def build_csv(filename="copenhagen_restaurants.csv"):
    businesses = search_restaurants()

    # Your exact variables as columns
    fieldnames = [
        "Business name",
        "Business address",
        "Category",
        "Phone number",
        "Average star rating",
        "Hours of operation",
        "Review count",
        "Closure status",
        "Yelp profile URL",
        "Yelp menu URL",
        "Hot & New Status",
        "Price",
        "Business website URL",
        "Review Highlights",
        "Business summary",
        "Customer Experience",
        "Ambience",
        "Best nights",
        "Noise level",
        "Outdoor seating",
        "Vegan options",
        "Vegetarian options",
        "Gluten-free options",
        "Alcohol served",
        "Happy hour special"
    ]

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for b in businesses:
            details = get_details(b["id"])
            reviews = get_reviews(b["id"])
            tags = extract_tags(reviews)

            row = {
                "Business name": b["name"],
                "Business address": " ".join(b["location"]["display_address"]),
                "Category": ", ".join([c["title"] for c in b["categories"]]),
                "Phone number": b.get("display_phone"),
                "Average star rating": b["rating"],
                "Hours of operation": str(details.get("hours")),
                "Review count": b["review_count"],
                "Closure status": b["is_closed"],
                "Yelp profile URL": b["url"],
                "Yelp menu URL": details.get("menu_url", ""),
                "Hot & New Status": "",  # not available
                "Price": b.get("price"),
                "Business website URL": details.get("url"),

                # Reviews
                "Review Highlights": " | ".join([r["text"] for r in reviews]),
                "Business summary": reviews[0]["text"] if reviews else "",
                "Customer Experience": reviews[0]["text"] if reviews else "",

                # Tags
                "Ambience": tags["ambience"],
                "Best nights": tags["best_nights"],
                "Noise level": tags["noise_level"],
                "Outdoor seating": tags["outdoor_seating"],
                "Vegan options": tags["vegan_options"],
                "Vegetarian options": tags["vegetarian_options"],
                "Gluten-free options": tags["gluten_free_options"],
                "Alcohol served": tags["alcohol_served"],
                "Happy hour special": tags["happy_hour_special"]
            }

            writer.writerow(row)

    print(f"Saved to {filename}")


if __name__ == "__main__":
    build_csv()