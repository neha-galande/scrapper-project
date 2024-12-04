import requests
import csv
import time

GITHUB_TOKEN = "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"
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}"
}

# Step 2: Set up parameters
CITY = "Mumbai"  # Replace with the desired city
MIN_FOLLOWERS = 50    # Replace with the desired minimum follower count

# Step 3: Function to fetch GitHub users
def fetch_users(city, followers, page=1):
    url = f"https://api.github.com/search/users?q=location:{city}+followers:>={followers}&page={page}"
    users = []
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        users = data.get("items", [])
    except Exception as e:
        print("Error fetching users:", e)
    return users

# Step 4: Function to clean and format company names
def clean_company_name(company):
    if not company:
        return ""
    company = company.strip()
    if company.startswith("@"):
        company = company[1:]
    return company.upper()

# Step 5: Function to fetch a user's repositories
def fetch_repositories(username):
    url = f"https://api.github.com/users/{username}/repos"
    repos = []
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        repos = response.json()
    except Exception as e:
        print(f"Error fetching repositories for {username}:", e)
    return repos[:500]

# Step 6: Write user data to CSV
def write_users_to_csv(users):
    with open("users.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["login", "name", "company", "location", "email", "hireable", "bio",
                         "public_repos", "followers", "following", "created_at"])
        for user in users:
            try:
                user_data = requests.get(f"https://api.github.com/users/{user['login']}", headers=headers).json()
                writer.writerow([
                    user_data.get("login", ""),
                    user_data.get("name", ""),
                    clean_company_name(user_data.get("company", "")),
                    user_data.get("location", ""),
                    user_data.get("email", ""),
                    user_data.get("hireable", ""),
                    user_data.get("bio", ""),
                    user_data.get("public_repos", ""),
                    user_data.get("followers", ""),
                    user_data.get("following", ""),
                    user_data.get("created_at", "")
                ])
                time.sleep(1)  # Delay to respect API rate limits
            except Exception as e:
                print(f"Error writing user {user['login']} to CSV:", e)

# Improved write_repositories_to_csv function
def write_repositories_to_csv(users):
    with open("repositories.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["login", "full_name", "created_at", "stargazers_count", "watchers_count",
                         "language", "has_projects", "has_wiki", "license_name"])
        for user in users:
            repos = fetch_repositories(user["login"])
            for repo in repos:
                license_name = repo.get("license", {}).get("key", "") if repo.get("license") else ""
                writer.writerow([
                    user["login"],
                    repo.get("full_name", ""),
                    repo.get("created_at", ""),
                    repo.get("stargazers_count", ""),
                    repo.get("watchers_count", ""),
                    repo.get("language", ""),
                    repo.get("has_projects", ""),
                    repo.get("has_wiki", ""),
                    license_name
                ])
                time.sleep(1)  # Delay to respect API rate limits

# Step 8: Execute the main program
if __name__ == "__main__":
    print(f"Fetching users in {CITY} with over {MIN_FOLLOWERS} followers...")
    all_users = []
    page = 1

    while True:
        users = fetch_users(CITY, MIN_FOLLOWERS, page)
        if not users:  # Break the loop if no more users are found
            break
        all_users.extend(users)
        page += 1

    print(f"Total users fetched: {len(all_users)}")
    print("Writing users to users.csv...")
    write_users_to_csv(all_users)
    print("Writing repositories to repositories.csv...")
    write_repositories_to_csv(all_users)
    print("Data collection complete.")
