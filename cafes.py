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


def search_businesses(location="Copenhagen", categories="restaurants,cafes,bakeries", limit=20):
    params = {
        "location": location,
        "categories": "cafes,bakeries",
        "limit": limit
    }
    res = requests.get(SEARCH_URL, headers=HEADERS, params=params)
    return res.json().get("businesses", [])


def get_details(business_id):
    return requests.get(DETAILS_URL.format(business_id), headers=HEADERS).json()


def get_reviews(business_id):
    return requests.get(REVIEWS_URL.format(business_id), headers=HEADERS).json().get("reviews", [])


def get_business_type(categories):
    mapping = {
        "cafes": "Cafe",
        "bakeries": "Bakery",
        "restaurants": "Restaurant"
    }

    labels = []
    for c in categories:
        if c["alias"] in mapping:
            labels.append(mapping[c["alias"]])

    return ", ".join(labels) if labels else "Other"


def extract_tags(reviews):
    text = " ".join([r["text"].lower() for r in reviews])

    def has(words):
        return any(w in text for w in words)

    return {
        "ambience": "cozy" if has(["cozy", "romantic"]) else None,
        "outdoor_seating": has(["outdoor", "patio"]),
        "vegan_options": has(["vegan"]),
        "vegetarian_options": has(["vegetarian"]),
        "gluten_free_options": has(["gluten-free"])
    }


def build_csv(filename="copenhagen_restaurants.csv"):
    businesses = search_businesses()

    fieldnames = [
        "Business name",
        "Business address",
        "Category",
        "Business Type",
        "Phone number",
        "Average star rating",
        "Hours of operation",
        "Review count",
        "Closure status",
        "Yelp profile URL",
        "Price",
        "Business website URL",
        "Review Highlights",
        "Business summary",
        "Customer Experience",
        "Ambience",
        "Outdoor seating",
        "Vegan options",
        "Vegetarian options",
        "Gluten-free options"
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
                "Business Type": get_business_type(b["categories"]),
                "Phone number": b.get("display_phone"),
                "Average star rating": b["rating"],
                "Hours of operation": str(details.get("hours")),
                "Review count": b["review_count"],
                "Closure status": b["is_closed"],
                "Yelp profile URL": b["url"],
                "Price": b.get("price"),
                "Business website URL": details.get("url"),

                "Review Highlights": " | ".join([r["text"] for r in reviews]),
                "Business summary": reviews[0]["text"] if reviews else "",
                "Customer Experience": reviews[0]["text"] if reviews else "",

                "Ambience": tags["ambience"],
                "Outdoor seating": tags["outdoor_seating"],
                "Vegan options": tags["vegan_options"],
                "Vegetarian options": tags["vegetarian_options"],
                "Gluten-free options": tags["gluten_free_options"]
            }

            writer.writerow(row)

    print(f"Saved to {filename}")


if __name__ == "__main__":
    build_csv(filename="copenhagen_cafes.csv")