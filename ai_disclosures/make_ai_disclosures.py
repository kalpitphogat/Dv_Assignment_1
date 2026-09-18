"""
DAS732 A1 - fill the course AI disclosure statement for each team member.

    python make_ai_disclosures.py

Reads the instructor's template (.docx) and writes one filled copy per member
next to itself. The layout follows the sample filing shared by a
classmate: Sections 1, 4 and 5 only (Sections 2 and 3 are dropped, since no web
dashboard was built and no Tableau AI feature was used), a "Learning Tableau"
line in place of Section 1's "None", and short descriptions.

The template is edited at the XML level rather than through python-docx, because
lxml is blocked by this machine's Application Control policy - and editing the
XML in place preserves the instructor's formatting exactly.

Each member should read their own copy, correct anything that does not match
what they personally did, and sign it. Section 5 is left exactly as the template
has it, and the chat-transcript link is left blank.
"""
from __future__ import annotations

import pathlib
import re
import sys
import zipfile

HERE = pathlib.Path(__file__).resolve().parent
OUT_DIR = HERE

# The instructor's blank template is not redistributed with this submission,
# so pass its path as the first argument, or drop a copy beside this script:
#     python make_ai_disclosures.py "path/to/AI-Disclosure-Statement.docx"
DEFAULT_TEMPLATE = HERE / "DAS732-T1-26-27-AI-Disclosure-Statement.docx"
TEMPLATE = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TEMPLATE

TICK = "\u2714"          # the mark used in the sample filing


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# --------------------------------------------------------------- content ---
# Section 1 boxes each member can tick, keyed by a fragment of the template line.
S1_TICKS = {
    "A": ["Learning Tableau", "Data cleaning", "Plot/Chart", "Debugging"],
    "B": ["Learning Tableau", "Data cleaning", "Plot/Chart", "Debugging"],
    "C": ["Learning Tableau", "Data cleaning", "Plot/Chart", "Statistical",
          "Debugging"],
}

S1_DESC = {
    "A": ("Claude was used during data preprocessing to write and refine the "
          "cleaning, restructuring and transformation steps applied to the "
          "EM-DAT dataset, and to generate the plotting code for the temporal "
          "figures. It was also used for troubleshooting errors encountered "
          "while running that code. The generated code and suggestions were "
          "reviewed, modified where necessary, and validated by me against the "
          "dataset before being used."),
    "B": ("Claude was used to write the code for the geographic figures - the "
          "country-level aggregations and the choropleth maps - and to generate "
          "the plotting boilerplate for the ranking and concentration charts. "
          "It was also used for troubleshooting errors encountered while "
          "running that code. The generated code and suggestions were reviewed, "
          "modified where necessary, and validated by me against the dataset "
          "before being used."),
    "C": ("Claude was used to write the code for the hazard impact figures and "
          "for the statistical calculations reported in the report - the "
          "log-linear trend fits and the rank-correlation test. It was also "
          "used for troubleshooting errors encountered while running that "
          "code. The generated code and suggestions were reviewed, modified "
          "where necessary, and validated by me against the dataset before "
          "being used."),
}

S4_TICKS = {
    "A": ["Outlining", "Drafting descriptions", "Proofreading", "docstrings"],
    "B": ["Outlining", "Drafting descriptions", "Proofreading"],
    "C": ["Outlining", "Drafting descriptions", "Translating statistical",
          "Proofreading", "docstrings"],
}

S4_DESC = {
    "A": ("Claude was used to help outline the structure of the report and to "
          "draft the descriptions of the patterns visible in my figures, which "
          "I then edited. It was also used for proofreading and formatting, and "
          "for generating docstrings and comments in the Python scripts. The "
          "choice of visualizations and the interpretation of the results were "
          "decided and verified by me, and every figure quoted in the report "
          "was checked against the dataset."),
    "B": ("Claude was used to help outline the structure of the report and to "
          "draft the descriptions of the patterns visible in my figures, which "
          "I then edited. It was also used for proofreading and formatting. The "
          "choice of visualizations and the interpretation of the results were "
          "decided and verified by me, and every figure quoted in the report "
          "was checked against the dataset."),
    "C": ("Claude was used to help outline the structure of the report, to "
          "draft the descriptions of the patterns visible in my figures, and to "
          "put the statistical results into plain language, which I then "
          "edited. It was also used for proofreading and formatting, and for "
          "generating docstrings and comments in the Python scripts. The choice "
          "of visualizations and the interpretation of the results were decided "
          "and verified by me, and every figure quoted in the report was "
          "checked against the dataset."),
}

MEMBERS = [
    ("A", "LAKSHYA JAIN", "BT2024044"),
    ("B", "ARNAV JAIN", "BT2024233"),
    ("C", "KALPIT", "BT2024093"),
]

P_RE = re.compile(r"<w:p[ >].*?</w:p>", re.S)
T_RE = re.compile(r"<w:t[^>]*>(.*?)</w:t>", re.S)


def ptext(p: str) -> str:
    return "".join(T_RE.findall(p))


def set_text(p: str, new: str) -> str:
    """Replace a paragraph's text, keeping its single run and formatting."""
    return T_RE.sub(lambda m: f'<w:t xml:space="preserve">{new}</w:t>', p, count=1)


def build(doc: str, key: str, name: str, roll: str) -> str:
    head, body, tail = doc.partition("<w:body>")
    paras = P_RE.findall(doc)
    out: list[str] = []

    section = 0
    skipping = False
    for p in paras:
        t = ptext(p)

        if t.startswith("## "):
            section = int(t.split(".")[0].replace("## ", "").strip())
            # Sections 2 and 3 are dropped, following the sample filing.
            skipping = section in (2, 3)
        if skipping:
            continue

        if t == "Name of Student:":
            p = set_text(p, f"Name of Student: {esc(name)}")
        elif t == "Roll Number:":
            p = set_text(p, f"Roll Number: {esc(roll)}")

        elif section == 1:
            if t.startswith("* **Tool(s) Used:**"):
                p = set_text(p, "* **Tool(s) Used:** Claude")
            elif t == "  * [ ] None":
                # the sample replaces Section 1's "None" with this line
                p = set_text(p, f"  * [{TICK}] Learning Tableau")
            elif t.startswith("  * [ ]"):
                if any(frag in t for frag in S1_TICKS[key]):
                    p = set_text(p, t.replace("[ ]", f"[{TICK}]", 1))
            elif t.startswith("* **Prompts Used"):
                p = set_text(p, "* **Prompts Used &amp; Modification Level:** "
                                + esc(S1_DESC[key]))

        elif section == 4:
            if t.startswith("* **Tool(s) Used:**"):
                p = set_text(p, "* **Tool(s) Used:** Claude")
            elif t.startswith("  * [ ]") and t != "  * [ ] None":
                if any(frag in t for frag in S4_TICKS[key]):
                    p = set_text(p, t.replace("[ ]", f"[{TICK}]", 1))
            elif t.startswith("* **Description of AI Involvement:**"):
                p = set_text(p, "* **Description of AI Involvement:** "
                                + esc(S4_DESC[key]))

        out.append(p)

    # reassemble: swap the original paragraph sequence for the edited one
    first, last = paras[0], paras[-1]
    start = doc.index(first)
    end = doc.index(last) + len(last)
    return doc[:start] + "".join(out) + doc[end:]


def main() -> int:
    if not TEMPLATE.exists():
        sys.exit(f"template not found: {TEMPLATE}")
    OUT_DIR.mkdir(exist_ok=True)

    src = zipfile.ZipFile(TEMPLATE)
    names = src.namelist()
    original = {n: src.read(n) for n in names}
    doc_xml = original["word/document.xml"].decode("utf-8")

    for key, name, roll in MEMBERS:
        filled = build(doc_xml, key, name, roll)
        safe = name.title().replace(" ", "_")
        out = OUT_DIR / f"AI_Disclosure_{safe}_{roll}.docx"
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for n in names:
                data = (filled.encode("utf-8") if n == "word/document.xml"
                        else original[n])
                z.writestr(n, data)
        print(f"  wrote ai_disclosures/{out.name}  "
              f"({filled.count(TICK)} ticked, sections 1/4/5)")

    print("\n  Read your own copy, correct anything that does not match what you "
          "personally\n  did, then sign it. Section 5 and the chat-transcript "
          "link are untouched.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
