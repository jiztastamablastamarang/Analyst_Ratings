import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from attr import attrs, attrib
import time
from datetime import datetime, date, timedelta
import dateparser
import json
import pandas as pd
# import ijson
import os
import glob
import re
from console_progressbar import ProgressBar
import concurrent.futures
from newspaper import Article, Config

#%%
start = time.monotonic()

# %%

# Clear and Paragraph
def Clear(text):
    if len(text) != 0:
        text = str(text)
        for i, char in enumerate(text):
            if not char.isspace():
                break
        text = text[i:]
        text = re.sub("\n{2,}", "\n", text)
        text = re.sub(r"(\()\s+", "(", text)
        text = re.sub(r"\s+(\))", ")", text)
        text = re.sub("[\s\t\v]*<p>([\s\t\r\v]*)", "", text)
        text = re.sub("[\s\t\r\v]*</p>([\s\t\r\v]*)", "\n", text)
        text = re.sub(r"“|”", '"', text)
        text = re.sub("&amp;", "&", text)
        text = re.sub("<match color='4'>", "", text)
        text = re.sub("</match>", "", text)
        text = re.sub("<[A-Za-z\/][^>]*>", '', text)
        return text
    else:
        return ""

# Paragraph

def HitParagraf(input, keywords):
    if type(input).__name__ in ('list', 'tuple'):
        text = '\n'.join([str(p) for p in input])
    else:
        text = str(input)
    text = re.sub('\r', '\n', text)
    ps = re.split('\n', text)
    text = [p for p in ps if any(p.lower().find(keyword.lower()) > -1 for keyword in keywords)]
    return list(set(text))

# Collect files from the path

def collect_excel(path_to: "path to files", ext: "file type"):
    import pandas as pd
    df = pd.DataFrame()
    files = glob.glob(os.path.join(f"{path_to}", f"*.{ext}"))

    collection = pd.DataFrame()
    for file in files:
        df = pd.read_excel(file, sheet_name="Sheet1")
        collection = collection.append(df, ignore_index=True)
    return collection
# %%
# Clear and Paragraph
HEADERS = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel '
                         'Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0',
           'Accept': 'text/html,application/xhtml+xml,'
                     'application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Cookie': '__utma=40499190.288645356.1626172703.16261'
                     '72703.1626172703.1; __utmc=40499190; __utmz=40499190.1627'
                     '172703.1.1.utmcsr=(direct)|utmccn=(direct)|'
                     'utmcmd=(none); __utmt=1; __qca=P0-462214369-16261727'
                     '03831; _ga=GA1.2.288645356.1626172703; _gid=GA1.2.4211'
                     '60026.1626172704; __aaxsc=1; coregval=ims; '
                     'slogin=1626172892; slogin=1626172892; _gat_gtag_UA_1'
                     '36162586_1=1; mnet_session_depth=10|1626172703923; '
                     'aasd=10|1626172704511; __utmb=40499190.13.10.1626172703'}

bad = set()
def fly_parser(url):
  try:
    text = requests.get(url, headers=HEADERS)
    if text.status_code != 200:
        text = requests.get(url, headers=HEADERS, timeout=3)
    text.encoding = "utf-8"  # кодировка кракозяблей
    text = text.text
    soup = BeautifulSoup(text, "html.parser")
    headline = soup.find("td", attrs={"class": "newsContent"})
    if headline is not None:
        headline = headline.find("h1").get_text()
        ps = soup.find("td", attrs={"class": "newsContent"}).find_all("p", attrs={'class': None})
        body = []
        for p in ps:
            body.append(p.get_text())
        body = "\n".join(body)
        date = soup.find("span", attrs={"class": "fpo_overlay fechaConAnio"}).contents[0]
        date = dateparser.parse(date, languages=["en"])
    else:
        headline = soup.find("article").find("h1").getText()
        body = []
        ps = soup.find("article").find_all("div")
        for p in ps:
            if len(p) > 0:
                body.append(p.get_text())
        body = "\n".join(body)
        try:
            date = soup.find("span", attrs={"id": "horaCompleta"}).getText()
            date = dateparser.parse(date, languages=["en"])
        except:
            date = None
    return date, url, headline, body
  except:
    bad.add(url)


def get_news(url):
    text = requests.get(url, headers=HEADERS)
    text.encoding = "utf-8"
    text = text.text
    soup = BeautifulSoup(text, "html.parser")
    n = soup.find("a", attrs={"href": re.compile("\d{7}$")})
    return int(n.get('href')[-7:])


# %% Main
columns = ["date", "URL", "source", "headline", "body", "summary"]
scraping_data = pd.DataFrame(columns=columns)

path = "g:/My Drive/ETF/"

keywords = set(["target price", "price target", "price objective", "objective price", " pt"])

try:
    n = get_news("https://thefly.com/news.php?onthefly=on")
    print(n)
except:
    n = 3381518

max = 1000000
workers = os.cpu_count()*5

url = "https://thefly.com/onthefly.php?id="
URLS = [f"{url}{n-m}" for m in range(max)]

# %% Work

with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
    results_2 = executor.map(fly_parser, URLS)
    executor.shutdown(wait=True)

# %% Unpack results:
k = 0
for r in results_2:
    try:
        date, url, headline, body = r
        summary = "\n".join(HitParagraf([headline, body], keywords))
        scraping_data = scraping_data.append({"date": date, "URL": url, "headline": headline, "source": "The Fly",
                                              "body": body, "summary": summary}, ignore_index=True)
    except:
        pass
        k += 1

#%%
end = time.monotonic()
print(f"Duration: {timedelta((end-start))}")


#%% SelfSave
def saveme (output, path):
    writer = pd.ExcelWriter(path, engine='xlsxwriter', options={'strings_to_urls': False})
    output.to_excel(writer)
    writer.close()
dataset = scraping_data
dataset = dataset.loc[dataset["body"].str.contains("|".join(keywords), case=False, regex=True)]
dataset = dataset.reset_index(drop=True)

#%%
bad_ = pd.DataFrame(bad)
saveme(bad_, f"{path}bad_url_{n-max}-{n}.xlsx")
saveme(scraping_data, f"{path}TheFly_{n-max}-{n}.xlsx")
saveme(dataset, f"{path}TheFly_relevant_{n-max}-{n}.xlsx")

