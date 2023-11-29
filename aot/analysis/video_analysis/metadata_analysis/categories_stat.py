import moten
import pickle
import yaml
import os
import aot
from pathlib import Path
import csv
from wordcloud import WordCloud


base_dir = Path(aot.__path__[0])
video_db_path = base_dir / "data/videos/database_originals.tsv"

# read tsv file
categories_count = {}
total = 0
with open(video_db_path, "r") as f:
    reader = csv.reader(f, delimiter="\t")
    video_db = list(reader)
    for row in video_db[1:]:
        category = row[1]
        total += 1
        if category not in categories_count:
            categories_count[category] = 1
        else:
            categories_count[category] += 1

print(categories_count)

freq_dic = {}
for key, value in categories_count.items():
    freq_dic[key] = value / total

print(freq_dic)

# make a wordcloud picture
wordcloud = WordCloud(background_color="white", max_words=1000)
wordcloud.generate_from_frequencies(freq_dic)
wordcloud.to_file("categories_wordcloud.png")
