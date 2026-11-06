"""Rebuild the Featured Projects table in README.md from the owner's public repos."""
import json
import os
import re
import sys
import urllib.request

OWNER = os.environ.get("GITHUB_REPOSITORY_OWNER", "singhkaushik550")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
START, END = "<!--PROJECTS:START-->", "<!--PROJECTS:END-->"
MAX_REPOS = 8
BT = chr(96)


def get(url):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-readme-bot"}
    if TOKEN:
        headers["Authorization"] = "Bearer " + TOKEN
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers)) as resp:
        return json.load(resp)


def cell(text):
    return (text or "").replace("|", "/").replace("\n", " ").strip()


repos = get("https://api.github.com/users/%s/repos?per_page=100&type=owner" % OWNER)
repos = [r for r in repos if not r["fork"] and not r["archived"] and r["name"].lower() != OWNER.lower()]
repos.sort(key=lambda r: r["pushed_at"], reverse=True)
repos = repos[:MAX_REPOS]

rows = ["| Project | What it does | Stack | Stars |", "|---|---|---|---|"]
for r in repos:
    stack = []
    if r.get("language"):
        stack.append(BT + r["language"] + BT)
    stack += [BT + t + BT for t in (r.get("topics") or [])[:3]]
    desc = cell(r.get("description")) or "Work in progress"
    rows.append("| [**%s**](%s) | %s | %s | %s |" % (r["name"], r["html_url"], desc, " ".join(stack) or "-", r["stargazers_count"]))

block = START + "\n" + "\n".join(rows) + "\n" + END

with open("README.md", encoding="utf-8") as fh:
    text = fh.read()

pattern = re.compile(re.escape(START) + ".*?" + re.escape(END), re.S)
if not pattern.search(text):
    sys.exit("Projects markers not found in README.md")

new_text = pattern.sub(lambda m: block, text)
if new_text != text:
    with open("README.md", "w", encoding="utf-8") as fh:
        fh.write(new_text)
    print("README updated with %d repos" % len(repos))
else:
    print("No changes")
