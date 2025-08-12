import os
import json
import time
import argparse
import requests
from dotenv import load_dotenv
from newspaper import Article
from openai import AzureOpenAI

# === Load environment variables ===
load_dotenv()

# === Validate environment variables ===
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
DEPLOYMENT_NAME = os.getenv("OPENAI_DEPLOYMENT_NAME")
TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")

if not all([SERPAPI_KEY, OPENAI_API_KEY, OPENAI_API_BASE, OPENAI_API_VERSION, DEPLOYMENT_NAME, TEAMS_WEBHOOK_URL]):
    raise EnvironmentError(" Missing one or more required environment variables.")

# === Azure OpenAI Client ===
client = AzureOpenAI(
    api_key=OPENAI_API_KEY,
    api_version=OPENAI_API_VERSION,
    azure_endpoint=OPENAI_API_BASE,
)

# === Send message to Microsoft Teams ===
def send_to_teams(message: str):
    webhook = os.getenv("TEAMS_WEBHOOK_URL")  # or hardcode if needed

    # Teams supports **bold**, *italic*, and `code`, as well as line breaks via \n
    payload = {
        "message": f"**🧠 Weekly AI Tools Digest**\n\n{message}"
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(webhook, headers=headers, data=json.dumps(payload))
        if response.status_code in [200, 202]:
            print("Message sent to Microsoft Teams!")
        else:
            print(f" Failed with status code: {response.status_code}")
            print("Response:", response.text)
    except Exception as e:
        print(" Error sending message:", e)


# === Search for AI tools using SerpAPI ===
def search_ai_articles(query="new AI tools launched this week", num_results=20):
    try:
        params = {
            "engine": "google",
            "q": query,
            "api_key": SERPAPI_KEY,
            "num": num_results,
            "hl": "en",
            "gl": "us",
            "tbs": "qdr:w",  # past week
        }
        res = requests.get("https://serpapi.com/search", params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
        return [r.get("link") for r in data.get("organic_results", [])]
    except requests.RequestException as e:
        print(f" Network error while fetching search results: {e}")
        return []

# === Summarize each article ===
def summarize_tool_article(content, source_url):
    prompt = f"""
Summarize the following article about a newly launched AI tool.

Format:
🔹 Tool Name:
🔹 Website:
🔹 Summary:
🔹 Key Features:
🔹 Pricing:
🔹 Category:
🔹 Source URL: {source_url}

Article:
\"\"\"{content}\"\"\"
"""
    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are an expert in analyzing and summarizing AI tools."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=800,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f" GPT error: {e}")
        return None

# === Main runner ===
def run_digest(max_tools=5, post_to_teams=False):

    urls = search_ai_articles(num_results=20)
    print(f" Found {len(urls)} initial results")

    filtered = [
        url for url in urls
        if all(x not in url for x in ["youtube.com", "instagram.com", "futurepedia", "trendhunter", "list", "directory"])
    ]
    print(f" Filtered {len(filtered)} usable articles\n")

    collected = []
    attempted = 0

    for url in filtered:
        if len(collected) >= max_tools:
            break

        print(f" Processing: {url}")
        attempted += 1
        try:
            article = Article(url)
            article.download()
            article.parse()
            content = article.text.strip()

            if not content:
                print(" Empty content, skipping...\n")
                continue

            summary = summarize_tool_article(content[:4000], url)
            if summary and "🔹 Tool Name:" in summary:
                print(summary)
                print("-" * 40)
                collected.append(summary)
            else:
                print("⚠️ No valid summary format, skipping...\n")

        except Exception as e:
            print(f" Error parsing article: {e}")
        time.sleep(2)

    if not collected:
        print(" No tools summarized.")
        return

    # Save locally
    formatted_message = "\n\n---\n\n".join(collected)

    with open("ai_tools_weekly_digest.txt", "w", encoding="utf-8") as f:
        f.write(formatted_message)

    # If you're posting to Teams, send formatted_message
    if post_to_teams:
        send_to_teams(f"🧠 Weekly AI Tools Digest\n\n{formatted_message}")

    print(" Saved summary locally as ai_tools_weekly_digest.txt")

# === CLI ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and summarize newly launched AI tools.")
    parser.add_argument("--max_tools", type=int, default=5, help="Maximum number of tools to summarize.")
 #   parser.add_argument("--post_to_teams", action="store_true", help="Send the summarized digest to Microsoft Teams.")
    args = parser.parse_args()

    run_digest(max_tools=args.max_tools)