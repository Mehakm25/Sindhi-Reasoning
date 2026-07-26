import gradio as gr
import requests
import pandas as pd
import os
from datetime import datetime

CSV_FILE = "wiki_data.csv"

def fetch_wikipedia_summary(page_name):
    S = requests.Session()
    URL = "https://sd.wikipedia.org/w/api.php"  # Sindhi Wikipedia

    PARAMS = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "exintro": True,
        "explaintext": True,
        "titles": page_name,
    }

    R = S.get(url=URL, params=PARAMS)
    DATA = R.json()
    pages = DATA["query"]["pages"]
    page = next(iter(pages.values()))

    if "missing" in page:
        return f"❌ Page '{page_name}' not found on Sindhi Wikipedia."

    title = page.get("title", "")
    summary = page.get("extract", "")
    page_id = page.get("pageid", "")
    url = f"https://sd.wikipedia.org/wiki/{title.replace(' ', '_')}"
    timestamp = datetime.now().isoformat()

    # Load or create DataFrame
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        new_id = df["id"].max() + 1
    else:
        df = pd.DataFrame(columns=["id", "title", "url", "summary", "timestamp"])
        new_id = 1

    # Append new row
    new_row = {
        "id": new_id,
        "title": title,
        "url": url,
        "summary": summary,
        "timestamp": timestamp,
    }
    df = df._append(new_row, ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

    return f"✅ Summary for '{title}' (in Sindhi) saved successfully!"


# Gradio UI
iface = gr.Interface(
    fn=fetch_wikipedia_summary,
    inputs=gr.Textbox(label="Wikipedia Page Title"),
    outputs=gr.Textbox(label="Status"),
    title="Wikipedia Summary Saver",
    description="Enter a Wikipedia page name to download the intro section and save it in a CSV file.",
)

if __name__ == "__main__":
    iface.launch()
