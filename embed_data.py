#!/usr/bin/env python3
"""Copy sikkim_db/sikkim_disasters.json into the <script id="disasters-data"> block of index.html.
Usage: python3 embed_data.py sikkim_disasters.json index.html"""
import json, re, sys
data_path, html_path = sys.argv[1], sys.argv[2]
data = json.load(open(data_path, encoding="utf-8"))
ids = [e["event_id"] for e in data]
assert len(ids) == len(set(ids)), "event_id values must be unique"
blob = json.dumps(data, ensure_ascii=False, indent=1).replace("<", "\\u003c")
html = open(html_path, encoding="utf-8").read()
pat = re.compile(r'(<script type="application/json" id="disasters-data">)(.*?)(</script>)', re.S)
assert pat.search(html), "disasters-data block not found"
html = pat.sub(lambda m: m.group(1) + "\n" + blob + "\n" + m.group(3), html, count=1)
open(html_path, "w", encoding="utf-8").write(html)
print(f"Embedded {len(data)} events into {html_path}")
