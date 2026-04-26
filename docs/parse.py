"""Parse result.txt (scraped HTML blobs) into a structured JSON dataset.

Output: docs/data.js  -- a JS file that exposes `window.NOMAD_DATA = [...]`,
loadable by the static visualization pages without a server.
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "result.txt")
OUT = os.path.join(ROOT, "docs", "data.js")


def short_province(name):
    """Normalize 所属省份 to the short form ECharts china map uses (e.g. 四川, 重庆)."""
    if not name:
        return ""
    s = name
    for suffix in ("维吾尔自治区", "壮族自治区", "回族自治区", "自治区", "特别行政区", "省", "市"):
        if s.endswith(suffix):
            s = s[: -len(suffix)]
            break
    return s


def num(text):
    """Extract first numeric token (supports negatives and decimals). Returns None if absent."""
    if text is None:
        return None
    m = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(m.group(0)) if m else None


def field(html, label):
    """Grab the text after `label[：:？?]` up to the closing </p> tag."""
    pat = re.compile(re.escape(label) + r"[：:？?]\s*([\s\S]*?)</p>")
    m = pat.search(html)
    return m.group(1).strip() if m else ""


def yesno(text):
    """Map 有/无 answer to True/False/None.

    Answer text is short (e.g. "有" / "无" / "有集中供暖" / "无集中供暖"),
    so prefer the answer's own 无/有 marker over substring scanning.
    """
    if not text:
        return None
    s = text.strip()
    if s.startswith("无") or s == "否":
        return False
    if s.startswith("有") or s == "是":
        return True
    if "无" in s:
        return False
    if "有" in s:
        return True
    return None


def admin_level(key):
    """Infer admin level from the GB code embedded in the key (e.g. '310100-2').

    Returns one of: 'prefecture' (xxXX00), 'county' (xxXXXX), or 'unknown'.
    """
    m = re.match(r"^(\d{6})", key or "")
    if not m:
        return "unknown"
    code = m.group(1)
    if code.endswith("0000"):
        return "province"
    if code.endswith("00"):
        return "prefecture"
    return "county"


def parse_entry(key, html):
    rec = {"key": key, "admin_level": admin_level(key)}

    # Coordinates + canonical city name from the gaode iframe.
    m = re.search(
        r"position=([\d.]+),([\d.]+)[^\"']*name=([^&\"'<]+)", html
    )
    if m:
        rec["lng"] = float(m.group(1))
        rec["lat"] = float(m.group(2))
        rec["name"] = m.group(3)
    else:
        rec["lng"] = rec["lat"] = None
        # Fallback: try to derive from dianping anchor 看看XXX本地生活
        m2 = re.search(r"看看([^<]+?)本地生活", html)
        rec["name"] = m2.group(1) if m2 else key

    rec["province"] = field(html, "所属省份")
    rec["province_short"] = short_province(rec["province"])
    rec["parent_city"] = field(html, "上级城市")
    rec["gdp"] = num(field(html, "最新GDP数据"))  # 亿元
    rec["population"] = num(field(html, "最新人口数据"))  # 万人
    rec["income"] = num(field(html, "当地城镇居民人均年可支配收入"))  # 元

    rec["temp_max"] = num(field(html, "年最高温度"))
    rec["temp_min"] = num(field(html, "年最低温度"))
    rec["feel_max"] = num(field(html, "年最高体感温度"))
    rec["feel_min"] = num(field(html, "年最低体感温度"))
    rec["temp_avg"] = num(field(html, "年平均温度"))
    rec["feel_avg"] = num(field(html, "年平均体感温度"))
    rec["humidity"] = num(field(html, "年平均湿度"))
    rec["rainy_days"] = num(field(html, "每年下雨天数"))
    rec["sunny_days"] = num(field(html, "每年晴天天数"))
    rec["summer_days"] = num(field(html, "预期每年夏日天数"))
    rec["winter_days"] = num(field(html, "预期每年冬日天数"))
    rec["windy_days"] = num(field(html, "每年大风天数"))
    rec["has_heating"] = yesno(field(html, "集中供暖情况"))

    rec["starbucks"] = yesno(field(html, "这里有星巴克吗"))
    rec["mcdonalds"] = yesno(field(html, "这里有麦当劳吗"))
    rec["kfc"] = yesno(field(html, "这里有肯德基吗"))
    rec["gym"] = yesno(field(html, "这里有健身房吗"))

    rec["bus_time"] = num(field(html, "乘坐公交到达上级城市所需时间"))
    rec["bus_distance"] = num(field(html, "乘坐公交到达上级城市所需里程"))
    rec["drive_time"] = num(field(html, "驾车到达上级城市所需时间"))
    rec["drive_distance"] = num(field(html, "驾车到达上级城市所需里程"))

    # 途径高铁: text like "C", "C,D" or "无" inside a <p>...<br/>VALUE</p> block.
    m = re.search(r"途径高铁[：:]\s*<br/>\s*([\s\S]*?)</p>", html)
    rail = m.group(1).strip() if m else ""
    rec["rail"] = None if not rail or rail == "无" else rail
    rec["airport"] = yesno(field(html, "是否有机场覆盖"))

    return rec


def main():
    with open(SRC, "r", encoding="utf-8") as f:
        raw = json.load(f)

    out = []
    for item in raw:
        try:
            out.append(parse_entry(item["key"], item["value"]))
        except Exception as exc:  # keep going on bad rows
            print(f"warn: failed {item.get('key')}: {exc}", file=sys.stderr)

    # Sort by GDP desc with None at the bottom for nicer default ordering.
    out.sort(key=lambda r: (r.get("gdp") is None, -(r.get("gdp") or 0)))

    js = "window.NOMAD_DATA = " + json.dumps(out, ensure_ascii=False) + ";\n"
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(js)
    print(f"wrote {len(out)} records to {OUT}")


if __name__ == "__main__":
    main()
