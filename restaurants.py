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

import time

NEIGHBORHOODS = [
    "Nørrebro, Copenhagen",
    "Vesterbro, Copenhagen",
    "Østerbro, Copenhagen",
    "Frederiksberg, Copenhagen",
    "Amager, Copenhagen",
    "Indre By, Copenhagen",
    "Christianshavn, Copenhagen",
    "Valby, Copenhagen",
    "Vanløse, Copenhagen",
    "Brønshøj, Copenhagen"
]

def search_businesses(
    location=NEIGHBORHOODS,
    categories="restaurants",
    limit=50,
    exclude_categories=None
):
    exclude_categories = exclude_categories or []

    all_businesses = []
    offset = 0
    MAX_TOTAL = 1000

    while offset < MAX_TOTAL:
        params = {
            "location": location,
            "categories": categories,
            "limit": limit,
            "offset": offset
        }

        res = requests.get(SEARCH_URL, headers=HEADERS, params=params)

        if res.status_code != 200:
            handle_yelp_error(res)
            break

        businesses = res.json().get("businesses", [])

        if len(businesses) < limit:
            break

        if not businesses:
            break

        for b in businesses:
            aliases = [c["alias"] for c in b["categories"]]

            if any(x in aliases for x in exclude_categories):
                continue

            all_businesses.append(b)

        offset += limit
        # time.sleep(0.)

    return all_businesses

def get_details(business_id):
    res = requests.get(DETAILS_URL.format(business_id), headers=HEADERS)
    if res.status_code != 200:
        handle_yelp_error(res)
        return {}
    return res.json()


def get_reviews(business_id):
    res = requests.get(REVIEWS_URL.format(business_id), headers=HEADERS)
    if res.status_code != 200:
        handle_yelp_error(res)
        return []
    return res.json().get("reviews", [])


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

def get_existing_ids(filename):
    if not os.path.exists(filename):
        return set()

    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return {row["Yelp ID"] for row in reader if row.get("Yelp ID")}

def get_existing_ids_from_files(*filenames):
    ids = set()

    for filename in filenames:
        if not os.path.exists(filename):
            continue

        with open(filename, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            ids.update(row["Yelp ID"] for row in reader if row.get("Yelp ID"))

    return ids

def handle_yelp_error(response):
    try:
        error_data = response.json().get("error", {})
        code = error_data.get("code")
        desc = error_data.get("description")

        print(f"Yelp API Error → {code}: {desc}")

        if code == "TOO_MANY_REQUESTS_PER_DAY":
            print("Daily API limit reached. Stop execution.")
            exit()

        elif code == "TOO_MANY_REQUESTS_PER_SECOND":
            print("Rate limit hit. Sleeping for 2 seconds...")
            time.sleep(2)

        elif code == "INVALID_API_KEY":
            print("Invalid API Key. Check your .env file.")
            exit()

        else:
            print("Unhandled Yelp error.")

    except Exception:
        print("Unknown error:", response.text)

# def build_csv(filename="copenhagen_restaurants.csv", categories="restaurants", exclude_files=None):
#     exclude_files = exclude_files or []

#     existing_ids = get_existing_ids_from_files(filename, *exclude_files)

#     businesses = search_businesses(categories=categories,
#                                    exclude_categories=["cafes", "bakeries", "coffee", "tea"]
#                                    if categories == "restaurants"
#                                    else [])

#     fieldnames = [
#         "Yelp ID",
#         "Business name",
#         "Business address",
#         "Category",
#         "Business Type",
#         "Phone number",
#         "Average star rating",
#         "Hours of operation",
#         "Review count",
#         "Closure status",
#         "Yelp profile URL",
#         "Price",
#         "Business website URL",
#         "Review Highlights",
#         "Business summary",
#         "Customer Experience",
#         "Ambience",
#         "Outdoor seating",
#         "Vegan options",
#         "Vegetarian options",
#         "Gluten-free options"
#     ]

#     file_exists = os.path.exists(filename)

#     with open(filename, mode="a", newline="", encoding="utf-8") as file:
#         writer = csv.DictWriter(file, fieldnames=fieldnames)

#         if not file_exists:
#             writer.writeheader()

#         for b in businesses:
#             if b["id"] in existing_ids:
#                 print(f"Skipping already saved: {b['name']}")
#                 continue

#             details = get_details(b["id"])
#             reviews = get_reviews(b["id"])
#             tags = extract_tags(reviews)

#             row = {
#                 "Yelp ID": b["id"],
#                 "Business name": b["name"],
#                 "Business address": " ".join(b["location"]["display_address"]),
#                 "Category": ", ".join([c["title"] for c in b["categories"]]),
#                 "Business Type": get_business_type(b["categories"]),
#                 "Phone number": b.get("display_phone"),
#                 "Average star rating": b["rating"],
#                 "Hours of operation": str(details.get("hours")),
#                 "Review count": b["review_count"],
#                 "Closure status": b["is_closed"],
#                 "Yelp profile URL": b["url"],
#                 "Price": b.get("price"),
#                 "Business website URL": details.get("url"),

#                 "Review Highlights": " | ".join([r["text"] for r in reviews]),
#                 "Business summary": reviews[0]["text"] if reviews else "",
#                 "Customer Experience": reviews[0]["text"] if reviews else "",

#                 "Ambience": tags["ambience"],
#                 "Outdoor seating": tags["outdoor_seating"],
#                 "Vegan options": tags["vegan_options"],
#                 "Vegetarian options": tags["vegetarian_options"],
#                 "Gluten-free options": tags["gluten_free_options"]
#             }

#             writer.writerow(row)
#             existing_ids.add(b["id"])

#             print(f"Saved: {b['name']}")
#             time.sleep(0.2)

#     print(f"Finished updating {filename}")
        

def build_csv_by_neighborhood(filename, categories, exclude_files=None):
    exclude_files = exclude_files or []
    existing_ids = get_existing_ids_from_files(filename, *exclude_files)

    for neighborhood in NEIGHBORHOODS:
        print(f"\nSearching in {neighborhood}...\n")

        businesses = search_businesses(
            location=neighborhood,
            categories=categories,
            exclude_categories=["cafes", "bakeries", "coffee", "tea"]
            if categories == "restaurants" else []
        )

        write_businesses_to_csv(filename, businesses, existing_ids)

def write_businesses_to_csv(filename, businesses, existing_ids):
    fieldnames = [
        "Yelp ID",
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

    file_exists = os.path.exists(filename)

    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for b in businesses:
            if b["id"] in existing_ids:
                continue

            details = get_details(b["id"])
            reviews = get_reviews(b["id"])
            tags = extract_tags(reviews)

            row = {
                "Business name": b["name"],
                "Yelp ID": b["id"],
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
            existing_ids.add(b["id"])

            print(f"Saved: {b['name']}")
            # time.sleep(0.2)


if __name__ == "__main__":
    # build_csv_by_neighborhood(
    #     filename="copenhagen_cafes.csv",
    #     categories="cafes,bakeries,coffee,tea"
    # )

    build_csv_by_neighborhood(
        filename="copenhagen_restaurants.csv",
        categories="restaurants",
        exclude_files=["copenhagen_cafes.csv"]
    )