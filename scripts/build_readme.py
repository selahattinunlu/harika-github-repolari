#!/usr/bin/env python3
"""README.md'deki kategori bölümlerini categories.json'a göre yeniden üretir.

Kaynak, README'nin en altındaki "Tüm liste (numaraya göre)" tablosudur.
Yeni repo eklerken veya link güncellerken sadece o tabloyu ve categories.json'u
düzenle, sonra `python3 scripts/build_readme.py` çalıştır.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
CATEGORIES = ROOT / "categories.json"

QUICK_FIND = "## Aradığını hızlı bul"
FULL_LIST = "## Tüm liste (numaraya göre)"
LEGACY_LIST = "## Liste"
TABLE_HEADER = (
    "| # | Repo | Kısaca ne işe yarıyor? | GitHub | Short | İnceleme |\n"
    "|---|---|---|---|---|---|"
)
ROW = re.compile(r"^\| (\d+) \|")


def anchor(title):
    # GitHub'ın başlık anchor'ları: küçük harf, noktalama ve emoji silinir, boşluk -> "-"
    return re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")


def main():
    lines = README.read_text(encoding="utf-8").splitlines()

    if FULL_LIST in lines:
        source = lines[lines.index(FULL_LIST):]
    else:
        source = lines[lines.index(LEGACY_LIST):]
    rows = {}
    for line in source:
        m = ROW.match(line)
        if m:
            rows[int(m.group(1))] = line

    for marker in (QUICK_FIND, LEGACY_LIST):
        if marker in lines:
            head = lines[: lines.index(marker)]
            break
    while head and not head[-1].strip():
        head.pop()

    categories = json.loads(CATEGORIES.read_text(encoding="utf-8"))
    used = [n for c in categories for n in c["repos"]]
    errors = []
    dupes = sorted({n for n in used if used.count(n) > 1})
    if dupes:
        errors.append(f"Birden fazla kategoride: {dupes}")
    missing = sorted(set(rows) - set(used))
    if missing:
        errors.append(f"Kategorisi olmayan repolar: {missing}")
    unknown = sorted(set(used) - set(rows))
    if unknown:
        errors.append(f"categories.json'da olup listede olmayan numaralar: {unknown}")
    if errors:
        sys.exit("\n".join(errors))

    out = head + [
        "",
        QUICK_FIND,
        "",
        "- **Short'taki numarayı biliyorsan** (ör. *Part 135*): en alttaki "
        f"[Tüm liste](#{anchor(FULL_LIST[3:])}) bölümünü aç, liste numara sırasıyla.",
        "- **Repo adını hatırlıyorsan:** `Ctrl+F` / `Cmd+F` ile adını ara (ör. `remotion`).",
        "- **Konuya göre bakıyorsan:** aşağıdaki kategorilerden birine tıkla. "
        "Her kategoride en yeni repolar en üstte.",
        "",
        "## Kategoriler",
        "",
    ]
    for c in categories:
        out.append(f"- [{c['title']}](#{anchor(c['title'])}) ({len(c['repos'])})")
    out.append("")
    for c in categories:
        out += [f"## {c['title']}", "", f"_{c['description']}_", "", TABLE_HEADER]
        out += [rows[n] for n in sorted(c["repos"], reverse=True)]
        out += ["", "[↑ Kategorilere dön](#kategoriler)", ""]
    out += [
        FULL_LIST,
        "",
        "<details>",
        f"<summary>{len(rows)} reponun tamamını numara sırasıyla göster</summary>",
        "",
        TABLE_HEADER,
    ]
    out += [rows[n] for n in sorted(rows)]
    out += ["", "</details>", ""]

    README.write_text("\n".join(out), encoding="utf-8")
    print(f"README güncellendi: {len(rows)} repo, {len(categories)} kategori")


if __name__ == "__main__":
    main()
