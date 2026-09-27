"""Tailored CVs. Each job gets a small spec file (headline, summary, which
projects and bullets, skill order). The CV is built only from
profile/cv_data.yaml, so every line stays true. Output is a single-column
Word file with standard headings, which applicant tracking systems read
well, plus a PDF made from it."""
import re
import shutil
import subprocess
from pathlib import Path

import yaml

from .checker import URL, _numbers
from .config import PROFILE_DIR, ROOT, fact_texts, load_yaml
from .text import slug

CV_DATA = PROFILE_DIR / "cv_data.yaml"
CV_DIR = ROOT / "output" / "cvs"
SPEC_DIR = CV_DIR / "specs"
FONT = "Arial"


class SpecError(Exception):
    pass


def load_data():
    return yaml.safe_load(CV_DATA.read_text(encoding="utf-8"))


def cv_filename(company, title):
    def part(s, n):
        return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")[:n] or "x"
    return f"Oluwatobi_Mayungbo_CV_{part(company, 30)}_{part(title, 40)}"


def spec_path(day, company, title):
    return SPEC_DIR / f"{day}_{slug(company, 30)}_{slug(title, 50)}.yaml"


def resolve(spec, data):
    """Turn a spec into the exact CV content, refusing anything not in the data."""
    headline = spec.get("headline")
    if headline in data["headlines"]:
        headline = data["headlines"][headline]
    elif headline not in data["headlines"].values():
        raise SpecError(f"headline {headline!r} is not one of the headlines in cv_data.yaml")
    groups = []
    for g in spec.get("skills", list(data["skills"])):
        gid, lead = (g, []) if isinstance(g, str) else (g["group"], g.get("lead", []))
        if gid not in data["skills"]:
            raise SpecError(f"unknown skill group {gid!r}")
        items = data["skills"][gid]["items"]
        for x in lead:
            if x not in items:
                raise SpecError(f"skill {x!r} is not in group {gid!r}")
        groups.append((data["skills"][gid]["label"], lead + [x for x in items if x not in lead]))
    projects = []
    for p in spec["projects"]:
        pid = p["id"] if isinstance(p, dict) else p
        if pid not in data["projects"]:
            raise SpecError(f"unknown project {pid!r}")
        proj = data["projects"][pid]
        ids = p.get("bullets", list(proj["bullets"])) if isinstance(p, dict) else list(proj["bullets"])
        for b in ids:
            if b not in proj["bullets"]:
                raise SpecError(f"project {pid!r} has no bullet {b!r}")
        projects.append({**proj, "bullets": [proj["bullets"][b] for b in ids]})
    experience = []
    exp_spec = spec.get("experience", {k: list(v["bullets"]) for k, v in data["experience"].items()})
    for eid, ids in exp_spec.items():
        if eid not in data["experience"]:
            raise SpecError(f"unknown experience {eid!r}")
        e = data["experience"][eid]
        for b in ids:
            if b not in e["bullets"]:
                raise SpecError(f"experience {eid!r} has no bullet {b!r}")
        experience.append({**e, "bullets": [e["bullets"][b] for b in ids]})
    return {
        "name": data["name"], "email": data["email"], "links": data["links"], "headline": headline,
        "summary": " ".join(spec["summary"].split()), "skills": groups, "projects": projects,
        "experience": experience, "education": data["education"], "certificates": data["certificates"],
    }


def check_content(cv, where="cv"):
    """Same rules as the letter checker, applied to the text we wrote for
    this CV (headline and summary), plus a check that Nigeria stays off."""
    rules = load_yaml("writing.yaml")
    facts = _numbers(fact_texts() + "\n" + CV_DATA.read_text(encoding="utf-8"))
    problems = []
    written = f"{cv['headline']}\n{cv['summary']}"
    for ch in rules["dash_chars"]:
        if ch in written:
            problems.append(f"{where}: dash character {ch!r} in headline or summary")
    if re.search(r"\s-{1,2}\s", written):
        problems.append(f"{where}: hyphen used as a dash in the summary")
    low = written.lower()
    for phrase in rules["banned_phrases"]:
        if re.search(r"(?<![a-z])" + re.escape(phrase.lower()) + r"(?![a-z])", low):
            problems.append(f"{where}: banned phrase {phrase!r} in summary")
    for num in sorted(_numbers(URL.sub(" ", written)) - facts):
        problems.append(f"{where}: number {num:g} is not in your CV or projects")
    words = len(cv["summary"].split())
    if not 25 <= words <= 75:
        problems.append(f"{where}: summary is {words} words; keep it between 25 and 75")
    visible = " ".join([cv["headline"], cv["summary"], *[" ".join(i) for _, i in cv["skills"]],
                        *[p["name"] + " " + " ".join(p["bullets"]) for p in cv["projects"]],
                        *[e["org"] + " " + " ".join(e["bullets"]) for e in cv["experience"]]])
    if re.search(r"niger", visible, re.I):
        problems.append(f"{where}: the word Nigeria appears on the CV")
    return problems


# ------------------------------------------------------------------ Word

def _hyperlink(paragraph, text, url, size):
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    part = paragraph.part
    r_id = part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
                          is_external=True)
    link = OxmlElement("w:hyperlink")
    link.set(qn("r:id"), r_id)
    run = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    for tag, val in (("w:rFonts", None), ("w:color", "1F4E79"), ("w:u", "single"), ("w:sz", str(int(size * 2)))):
        el = OxmlElement(tag)
        if tag == "w:rFonts":
            el.set(qn("w:ascii"), FONT)
            el.set(qn("w:hAnsi"), FONT)
        else:
            el.set(qn("w:val"), val)
        rpr.append(el)
    run.append(rpr)
    t = OxmlElement("w:t")
    t.text = text
    run.append(t)
    link.append(run)
    paragraph._p.append(link)


def _rule_below(paragraph):
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    ppr = paragraph._p.get_or_add_pPr()
    bdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    for k, v in (("w:val", "single"), ("w:sz", "6"), ("w:space", "1"), ("w:color", "808080")):
        bottom.set(qn(k), v)
    bdr.append(bottom)
    ppr.append(bdr)


def build_docx(cv, path):
    from docx import Document
    from docx.enum.text import WD_TAB_ALIGNMENT
    from docx.shared import Inches, Pt, RGBColor

    doc = Document()
    for s in doc.sections:
        s.left_margin = s.right_margin = Inches(0.7)
        s.top_margin = s.bottom_margin = Inches(0.6)
    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = Pt(10)
    normal.paragraph_format.space_after = Pt(0)
    normal.paragraph_format.space_before = Pt(0)
    rpr = normal.element.get_or_add_rPr()
    rpr.get_or_add_rFonts().set("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia", FONT)
    width = doc.sections[0].page_width - doc.sections[0].left_margin - doc.sections[0].right_margin

    def para(text="", size=10, bold=False, italic=False, after=0, before=0, color=None):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(after)
        p.paragraph_format.space_before = Pt(before)
        if text:
            r = p.add_run(text)
            r.font.size = Pt(size)
            r.bold = bold
            r.italic = italic
            if color:
                r.font.color.rgb = RGBColor.from_string(color)
        return p

    def heading(text):
        p = para(text.upper(), size=10.5, bold=True, before=9, after=3, color="1F3864")
        _rule_below(p)

    def bullet(text):
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_after = Pt(1.5)
        p.paragraph_format.left_indent = Inches(0.22)
        r = p.add_run(text)
        r.font.size = Pt(9.5)

    para(cv["name"], size=18, bold=True, color="1F3864")
    para(cv["headline"], size=11, after=2, color="404040")
    contact = para(size=9.5, after=2)
    r = contact.add_run(cv["email"] + "  |  ")
    r.font.size = Pt(9.5)
    for i, link in enumerate(cv["links"]):
        _hyperlink(contact, link["text"], link["url"], 9.5)
        if i < len(cv["links"]) - 1:
            contact.add_run("  |  ").font.size = Pt(9.5)

    heading("Summary")
    para(cv["summary"], size=10, after=0)

    heading("Skills")
    for label, items in cv["skills"]:
        p = para(after=1.5)
        r = p.add_run(label + ": ")
        r.bold = True
        r.font.size = Pt(9.5)
        p.add_run(", ".join(items)).font.size = Pt(9.5)

    heading("Projects")
    for n, proj in enumerate(cv["projects"]):
        p = para(before=0 if n == 0 else 5, after=0)
        r = p.add_run(proj["name"])
        r.bold = True
        r.font.size = Pt(10)
        for link in proj.get("links", []):
            p.add_run("  |  ").font.size = Pt(9.5)
            _hyperlink(p, link["text"], link["url"], 9.5)
        para("Tech: " + proj["stack"], size=9, italic=True, after=1.5, color="404040")
        for b in proj["bullets"]:
            bullet(b)

    heading("Experience")
    for n, e in enumerate(cv["experience"]):
        p = para(before=0 if n == 0 else 5, after=1)
        p.paragraph_format.tab_stops.add_tab_stop(width, WD_TAB_ALIGNMENT.RIGHT)
        r = p.add_run(f"{e['role']}, {e['org']}")
        r.bold = True
        p.add_run("\t" + e["dates"]).font.size = Pt(9.5)
        for b in e["bullets"]:
            bullet(b)

    heading("Education")
    for ed in cv["education"]:
        p = para(after=1)
        p.paragraph_format.tab_stops.add_tab_stop(width, WD_TAB_ALIGNMENT.RIGHT)
        r = p.add_run(f"{ed['degree']}, {ed['school']}")
        r.bold = True
        p.add_run("\t" + ed["dates"]).font.size = Pt(9.5)

    heading("Certifications")
    for c in cv["certificates"]:
        bullet(c)

    props = doc.core_properties
    props.author = cv["name"]
    props.title = f"{cv['name']} CV"
    doc.save(path)


def to_pdf(docx_paths, out_dir):
    """Convert with LibreOffice when it is installed. Returns True if done."""
    exe = shutil.which("soffice") or shutil.which("libreoffice")
    if not exe or not docx_paths:
        return False
    subprocess.run([exe, "--headless", "--convert-to", "pdf", "--outdir", str(out_dir), *map(str, docx_paths)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=600)
    return True


def build_all(conn=None, only=None, log=print):
    """Build a CV for every spec in output/cvs/specs (or only the given ones)."""
    data = load_data()
    CV_DIR.mkdir(parents=True, exist_ok=True)
    specs = sorted(SPEC_DIR.glob("*.yaml")) if only is None else only
    built, problems = [], []
    for sp in specs:
        spec = yaml.safe_load(sp.read_text(encoding="utf-8"))
        try:
            cv = resolve(spec, data)
        except (SpecError, KeyError) as e:
            problems.append(f"{sp.name}: {e}")
            continue
        issues = check_content(cv, sp.name)
        if issues:
            problems += issues
            continue
        name = cv_filename(spec["company"], spec["title"])
        docx_path = CV_DIR / f"{name}.docx"
        build_docx(cv, docx_path)
        built.append((spec, docx_path))
    if built:
        to_pdf([d for _, d in built], CV_DIR)
    if conn is not None:
        for spec, d in built:
            conn.execute("UPDATE jobs SET cv_file = ? WHERE id = ?", (d.relative_to(ROOT).as_posix(), spec["job_id"]))
        conn.commit()
    for p in problems:
        log("  " + p)
    log(f"Built {len(built)} CVs in {CV_DIR.relative_to(ROOT)}" + (f", {len(problems)} problems" if problems else ""))
    return built, problems
