import csv, json
from pathlib import Path
import sys
import shutil

base_path = Path(f"./{sys.argv[1]}")
# out_path = Path("./html_out/result.html").absolute()
images_loc = Path("./images").absolute()

def tweets():
    with open(base_path / 'items_threads.json', encoding='utf-8') as file:
        for row in file.readlines():
            result = json.loads(row)
            yield result
    #     reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    #     for row in reader:
    #         if row[0] == 'date':
    #             continue
    #         yield eval(row[-2]) if row[-2] else [],row[-1]

def fixed_tweets(tweets):
    for t in tweets:
        images = t["images"]
        files = t["files"]
        html = t["html"]

        for im in images:
            fixed_url = im["url"].replace('https://nitter.it','')
            print(im["url"],fixed_url)
            html = html.replace(fixed_url, "..\\images/"+ im["path"])

        for f in files:
            fixed_url = f["url"].replace('https://nitter.it','')
            html = html.replace(fixed_url, "videos/"+ f["path"])

        t["html"] = html
        yield t

def take_n(n, gen):
    for i in range(n):
        yield from gen

t = fixed_tweets(tweets())

with open("template/template.html", encoding="utf-8") as f:
    template = f.readlines()

n=1
go = True
while go:
    item = next(t)
    url = item["link"]
    id = url.split("/")[-1].replace("#m","")
    ( base_path / f"threads" ).mkdir(exists_ok=True)
    with open(base_path / f"threads/thread.{id}.html", "w", encoding="utf-8") as f:
        for line in template:
            if "TIMELINE" in line:
                break
            line = line.replace('href="','href="..\\')
            line = line.replace('src="','src="..\\')
            f.write(line)
        f.write(item["html"])
        # for j in range(200):
        #     try:
        #         item = next(t)
        #     except StopIteration:
        #         go = False
        #         break
        #     if " thread\">" in item and not in_thread:
        #         f.write("<div class=\"thread-line\">")
        #         in_thread = True
        #     f.write(item)
        #     if " thread\">" not in item and in_thread:
        #         f.write("</div>")
        #         in_thread = False
        f.write(f"""</div><div class="show-more"><a href="result.{n+1}.html">Older...</a></div></div></div>""")
    n = n + 1

for p in Path("template").glob("*/"):
    if p.is_file():
        continue
    shutil.copytree(p, base_path / p.name, dirs_exist_ok=True) 
