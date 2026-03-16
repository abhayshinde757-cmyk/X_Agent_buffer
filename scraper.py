import time
import re
from collections import Counter
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def scrape_hashtag_posts(hashtag, max_posts=20):

    chrome_options = Options()

    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(r"user-data-dir=D:\selenium_profile")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    driver.get("https://x.com/home")

    time.sleep(5)

    if "login" in driver.current_url:
        input("Log into your X account in the browser, then press ENTER here...")

    search_url = f"https://x.com/search?q=%23{hashtag}&src=typed_query&f=live"

    driver.get(search_url)

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
    )

    posts = []

    elements = driver.find_elements(By.CSS_SELECTOR, "article")

    for el in elements:

        text = el.text

        if text and len(text) > 20:
            posts.append(text)

        if len(posts) >= max_posts:
                break

    driver.quit()

    return posts


# ----------------------------
# ANALYSIS AGENTS
# ----------------------------

def event_buzz_tracker(posts, hashtag):
    print("\nEVENT BUZZ SUMMARY")
    print("Total posts mentioning hashtag:", len(posts))
    unique_users = set()

    for p in posts:
        lines = p.split("\n")
        if len(lines) > 0:
            unique_users.add(lines[0])

    print("Unique contributors:", len(unique_users))


def identify_potential_attendees(posts):

    keywords = [
        "attending",
        "looking forward",
        "excited for",
        "anyone attending",
        "joining"
    ]

    attendees = []

    for p in posts:
        lower = p.lower()
        for k in keywords:
            if k in lower:
                attendees.append(p)
                break

    print("\nPOTENTIAL ATTENDEES")
    for a in attendees:
        print("-", a[:150])


def speaker_reputation_monitor(posts, speaker_name):

    mentions = []

    for p in posts:
        if speaker_name.lower() in p.lower():
            mentions.append(p)

    print("\nSPEAKER REPUTATION MENTIONS:", len(mentions))

    for m in mentions[:5]:
        print("-", m[:150])


def topic_trend_analysis(posts):

    words = []

    for p in posts:
        tokens = re.findall(r'\b[A-Za-z]{4,}\b', p.lower())
        words.extend(tokens)

    counter = Counter(words)

    print("\nTRENDING TOPICS")
    for word, count in counter.most_common(10):
        print(word, ":", count)


def best_tweets(posts):

    ranked = sorted(posts, key=len, reverse=True)

    print("\nTOP EVENT TWEETS")
    for t in ranked[:5]:
        print("-", t[:200])


def question_mining(posts):

    questions = []

    for p in posts:
        if "?" in p:
            questions.append(p)

    print("\nQUESTIONS FROM AUDIENCE")

    for q in questions:
        print("-", q[:150])


def sentiment_analysis(posts):

    positive_words = ["great", "amazing", "love", "awesome", "excited"]
    negative_words = ["bad", "boring", "crowded", "disappointing"]

    pos = 0
    neg = 0

    for p in posts:

        lower = p.lower()

        if any(w in lower for w in positive_words):
            pos += 1

        if any(w in lower for w in negative_words):
            neg += 1

    total = len(posts)

    if total == 0:
        return

    print("\nSENTIMENT SUMMARY")
    print("Positive:", round(pos/total*100, 2), "%")
    print("Negative:", round(neg/total*100, 2), "%")
    print("Neutral:", round((total-pos-neg)/total*100, 2), "%")


def photo_detector(posts):

    photos = []

    for p in posts:
        if "pic.twitter.com" in p:
            photos.append(p)

    print("\nPOSTS WITH PHOTOS")

    for p in photos:
        print("-", p[:150])


def event_feedback(posts):

    feedback_categories = {
        "content": ["great session", "amazing talk"],
        "venue": ["crowded", "venue", "hall"],
        "speaker": ["speaker", "talk"],
        "networking": ["meet", "network"]
    }

    print("\nEVENT FEEDBACK SUMMARY")

    for category, words in feedback_categories.items():

        matches = []

        for p in posts:
            for w in words:
                if w in p.lower():
                    matches.append(p)
                    break

        print(category, ":", len(matches))


def event_advocates(posts):

    user_counts = Counter()

    for p in posts:
        lines = p.split("\n")
        if len(lines) > 0:
            user = lines[0]
            user_counts[user] += 1

    print("\nEVENT ADVOCATES")

    for user, count in user_counts.most_common(5):
        print(user, "tweeted", count, "times")


def event_impact_report(posts):

    print("\nEVENT IMPACT REPORT")

    users = set()

    for p in posts:
        lines = p.split("\n")
        if len(lines) > 0:
            users.add(lines[0])

    print("Total tweets:", len(posts))
    print("Unique contributors:", len(users))


# ----------------------------
# MAIN EXECUTION
# ----------------------------

if __name__ == "__main__":

    hashtag = input("Enter hashtag to search: ")

    posts = scrape_hashtag_posts(hashtag, 20)

    print("\nCOLLECTED POSTS:", len(posts))

    event_buzz_tracker(posts, hashtag)

    identify_potential_attendees(posts)

    topic_trend_analysis(posts)

    best_tweets(posts)

    question_mining(posts)

    sentiment_analysis(posts)

    photo_detector(posts)

    event_feedback(posts)

    event_advocates(posts)

    event_impact_report(posts)