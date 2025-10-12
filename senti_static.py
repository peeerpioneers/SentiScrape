# senti_static.py

import sys, math
from datetime import datetime, timedelta

import pandas as pd

# 1) Configuration — tweak these thresholds as needed
POST_STD_MULTIPLIER    = 2.0    # drop users with posts > mean+2·std
BASHER_RATIO           = 0.8    # drop users ≥80% negative comments
MIN_COMMENT_LEN        = 5      # drop comments shorter than 5 chars
SCRAPE_VOLUME_TARGET   = 200    # for scrape_conf → 100% at 200 comments
MODEL_CONFIDENCE       = 0.70   # assume VADER ~70% accurate on short text

# 2) Sentiment setup
try:
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    nltk.download("vader_lexicon", quiet=True)
except ImportError:
    print("🚫 Please install nltk: pip install nltk")
    sys.exit(1)

sid = SentimentIntensityAnalyzer()


def fetch_comments(ticker):
    """
    TODO: Replace this stub with your real scraper (Playwright/Spot.IM).
    Must return a DataFrame with columns: ['timestamp','text','user'].
    """
    return pd.DataFrame(columns=["timestamp", "text", "user"])


def filter_bots_and_bashers(df):
    raw_cnt = len(df)

    # drop exact text duplicates
    df = df.drop_duplicates(subset=["text"])

    # drop super-posters
    counts = df["user"].value_counts()
    cutoff = counts.mean() + POST_STD_MULTIPLIER * counts.std()
    df = df[~df["user"].isin(counts[counts > cutoff].index)]

    # drop bashers: users with ≥80% negative & post-count ≥ median
    temp = df.copy()
    temp["score"] = temp["text"].apply(
        lambda t: sid.polarity_scores(str(t))["compound"]
    )
    neg = temp[temp["score"] < -0.05]["user"].value_counts()
    tot = temp["user"].value_counts()
    median_posts = tot.median() or 1
    bashers = [u for u, n in neg.items()
               if n/tot[u] >= BASHER_RATIO and tot[u] >= median_posts]
    df = df[~df["user"].isin(bashers)]

    # drop too-short comments
    df = df[df["text"].str.len() >= MIN_COMMENT_LEN]

    return df.reset_index(drop=True), raw_cnt, len(df)


def classify_sentiment(text):
    c = sid.polarity_scores(str(text))["compound"]
    if c > 0.05:   return "positive"
    if c < -0.05:  return "negative"
    return "neutral"


def wilson_interval(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    denom = 1 + z*z/n
    centre = p + z*z/(2*n)
    margin = z * math.sqrt((p*(1-p) + z*z/(4*n)) / n)
    return (centre - margin)/denom, (centre + margin)/denom


def main():
    # ── 1) get ticker
    ticker = input("Enter a stock ticker (e.g. TSLA): ").strip().upper()
    if not (ticker.isalpha() and len(ticker) <= 5):
        print("❌ Invalid ticker format. Exiting.")
        return

    # ── 2) fetch raw comments
    print(f"\n🔍 Fetching comments for {ticker}…")
    df = fetch_comments(ticker)
    if df.empty:
        print(f"⚠ No comments found for {ticker}.")
        return
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df.dropna(subset=["timestamp","text"], inplace=True)

    # ── 3) filter bots & bashers
    df, raw_cnt, filt_cnt = filter_bots_and_bashers(df)

    # ── 4) keep last 30 days
    cutoff = datetime.now() - timedelta(days=30)
    df = df[df["timestamp"] >= cutoff]
    if df.empty:
        print(f"⚠ No comments in the last 30 days for {ticker}.")
        return

    # ── 5) sentiment + daily aggregation
    df["sentiment"] = df["text"].apply(classify_sentiment)
    df["date"] = df["timestamp"].dt.date

    daily = df.groupby("date")["sentiment"].value_counts().unstack(fill_value=0)
    for col in ("positive","negative"):
        daily.setdefault(col, 0)
    daily["total"] = daily.sum(axis=1)

    table = (daily[["total","positive","negative"]]
             .reset_index()
             .assign(ticker=ticker)
             .loc[:, ["date","ticker","total","positive","negative"]]
             .sort_values("date"))

    # ── 6) next-day probability + CI
    N = table["total"].sum()
    K = table["positive"].sum()
    p_up = (K/N) if N else 0
    lower, upper = wilson_interval(K, N)

    # ── 7) compute Data-Confidence
    scrape_conf = min(1.0, filt_cnt / SCRAPE_VOLUME_TARGET)
    user_conf   = filt_cnt / raw_cnt if raw_cnt else 0
    model_conf  = MODEL_CONFIDENCE
    data_conf   = scrape_conf * user_conf * model_conf

    # ── 8) print results
    print("\nDate        Ticker  Total  Pos  Neg")
    print("-------------------------------------")
    for _, r in table.iterrows():
        print(f"{r['date']}  {r['ticker']:6}  {r['total']:5}  "
              f"{r['positive']:4}  {r['negative']:4}")

    print("\n▶ Next-day Up Probability:")
    print(f"   p_up = {p_up:.0%}  (95% CI: {lower:.0%} – {upper:.0%})")
    print(f"   Data-Confidence ≈ {data_conf:.0%}")
    print(f"     • Scrape conf: {scrape_conf:.0%} "
          f"({filt_cnt}/{SCRAPE_VOLUME_TARGET})")
    print(f"     • User conf:   {user_conf:.0%} ({filt_cnt}/{raw_cnt})")
    print(f"     • Model conf:  {model_conf:.0%}")

    # ── 9) done
    print("\n✅ Done. Fill in `fetch_comments()` and enjoy your static report.")

if __name__ == "__main__":
    main()
