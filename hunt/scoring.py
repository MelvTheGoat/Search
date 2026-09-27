"""Fit score from 0 to 100, all local: MiniLM embeddings plus simple rules."""
import re
import sqlite3

import numpy as np

from .config import DATA_DIR, fact_texts, load_yaml
from .text import sha

# ---------------------------------------------------------------- filter


def is_relevant(title, description, cfg):
    """Step 2: keep jobs about data, ML or AI. Drops only clear misses."""
    f = cfg["filter"]
    t = title or ""
    if any(re.search(p, t, re.I) for p in f["drop_titles"]):
        return False
    if any(re.search(p, t, re.I) for p in f["keep_titles"]):
        return True
    if re.search(f["engineer_titles"], t, re.I):
        hits = len(re.findall(f["ml_words"], description or "", re.I))
        return hits >= f["min_ml_words"]
    return False


# ----------------------------------------------------------------- level

_TITLE_LEVELS = [
    ("intern", r"\bintern(ship)?s?\b|\bco-?op\b|\bplacement\b|\bapprentice|\bwerkstudent|\bpraktik|\bstagiaire|\btrainee\b"),
    ("manager", r"\bmanager\b|\bhead of\b|\bdirector\b|\bvp\b|\bvice president\b|\bchief\b"),
    ("principal", r"\bprincipal\b|\bdistinguished\b|\bfellow\b(?!ship)|\barchitect\b"),
    ("staff", r"\bstaff\b"),
    ("lead", r"\blead\b|\btech lead\b"),
    ("senior", r"\bsenior\b|\bsr\.?\b|\b(engineer|scientist|analyst|developer)\s+(iii|iv|v|3|4|5)\b|\bl[5-7]\b|\bexpert\b"),
    ("graduate", r"\bgraduate\b|\bnew grad|\bgrad\b|\bcampus\b|\buniversity\b|\bearly[- ]career\b|\bresidency\b|\bresident\b|\bfellowship\b"),
    ("entry", r"\bentry[- ]level\b|\bentry\b"),
    ("junior", r"\bjunior\b|\bjr\.?\b|\bassociate\b(?!\s+(director|principal|manager|partner))|\b(engineer|scientist|analyst|developer)\s+(i|1)\b|\bl[1-3]\b"),
    ("mid", r"\bmid[- ]?level\b|\bmid\b|\bintermediate\b|\b(engineer|scientist|analyst|developer)\s+(ii|2)\b|\bl4\b"),
]

_YEARS = re.compile(r"(\d{1,2})\s*\+?\s*(?:(?:-|to|–)\s*\d{1,2}\s*\+?\s*)?(?:years|yrs)", re.I)


def required_years(text):
    """Years of experience the post asks for. Uses the bachelor's figure
    when the post gives one per degree ("BS with 4-8 years"), else the
    first figure in the first sentence about experience."""
    for sent in re.split(r"(?<=[.!?])\s+|\n", text or ""):
        if not re.search(r"experience|years of", sent, re.I):
            continue
        m = re.search(r"\b(bs|ba|b\.s\.|bachelor'?s?)\b[^.;]{0,25}?(\d{1,2})\s*\+?\s*(?:(?:-|to|–)\s*\d{1,2}\s*\+?\s*)?(?:years|yrs)", sent, re.I)
        if m:
            return int(m.group(2))
        m = _YEARS.search(sent)
        if m and int(m.group(1)) <= 20:
            return int(m.group(1))
    return None


def detect_level(title, description=""):
    """Return (level, stretch). Title words win; else use years of experience."""
    t = title or ""
    for level, pat in _TITLE_LEVELS:
        if re.search(pat, t, re.I):
            return level, level == "mid"
    d = description or ""
    if re.search(r"new grad|recent graduate|entry[- ]level|graduate programme|graduate program|no experience required", d, re.I):
        return "entry", False
    y = required_years(d)
    if y is not None:
        if y >= 5:
            return "senior", False
        if y >= 3:
            return "mid", True
        return "junior", False
    return "unspecified", False


# ---------------------------------------------------------------- skills


class Skills:
    def __init__(self, table=None):
        table = table or load_yaml("skills.yaml")
        self.rules = []
        for name, spec in table.items():
            if isinstance(spec, dict):
                flags = 0 if spec.get("case_sensitive") else re.I
                pats = spec["patterns"]
            else:
                flags, pats = re.I, spec
            self.rules.append((str(name), [re.compile(p, flags) for p in pats]))

    def find(self, text):
        text = text or ""
        return [name for name, pats in self.rules if any(p.search(text) for p in pats)]


# ------------------------------------------------------------ embeddings


class Embedder:
    """MiniLM on CPU, with an SQLite cache so re-runs are fast.
    If the model cannot be loaded, falls back to a simple word-hash vector
    and says so."""

    def __init__(self, model_name="all-MiniLM-L6-v2", cache_path=None, log=print):
        self.model_name = model_name
        self.log = log
        self._model = None
        self.fallback = False
        self.cache_path = cache_path or DATA_DIR / "embeddings.db"
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.cache_path)
        self.db.execute("CREATE TABLE IF NOT EXISTS emb (k TEXT PRIMARY KEY, v BLOB)")

    def _load(self):
        if self._model is not None or self.fallback:
            return
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name, device="cpu")
        except Exception as e:  # noqa: BLE001
            self.log(f"  WARNING: could not load {self.model_name} ({str(e)[:120]}).")
            self.log("  Using a simple word-overlap fallback. Scores will be rougher until the model downloads.")
            self.fallback = True

    def _tag(self):
        return "hash-v1" if self.fallback else self.model_name

    def encode(self, texts):
        """Unit vectors for each text, from cache when possible."""
        self._load()
        keys = [sha(self._tag() + "|" + t, 24) for t in texts]
        out = [None] * len(texts)
        rows = {}
        for i in range(0, len(keys), 500):
            part = keys[i:i + 500]
            q = "SELECT k, v FROM emb WHERE k IN (%s)" % ",".join("?" * len(part))
            rows.update(dict(self.db.execute(q, part).fetchall()))
        todo = []
        for i, k in enumerate(keys):
            if k in rows:
                out[i] = np.frombuffer(rows[k], dtype=np.float32)
            else:
                todo.append(i)
        if todo:
            new = self._embed([texts[i] for i in todo])
            self.db.executemany("INSERT OR REPLACE INTO emb VALUES (?, ?)",
                                [(keys[i], new[j].astype(np.float32).tobytes()) for j, i in enumerate(todo)])
            self.db.commit()
            for j, i in enumerate(todo):
                out[i] = new[j].astype(np.float32)
        return np.vstack(out) if out else np.zeros((0, 384), dtype=np.float32)

    def _embed(self, texts):
        if not self.fallback:
            return self._model.encode(texts, batch_size=32, normalize_embeddings=True, show_progress_bar=len(texts) > 200)
        dim = 4096
        vecs = np.zeros((len(texts), dim), dtype=np.float32)
        for r, t in enumerate(texts):
            words = re.findall(r"[a-z][a-z+#]+", t.lower())
            for w in words + [a + " " + b for a, b in zip(words, words[1:])]:
                vecs[r, int(sha(w, 8), 16) % dim] += 1.0
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        return vecs / np.maximum(norms, 1e-9)


def chunk_words(text, size, max_chunks):
    words = (text or "").split()
    chunks = [" ".join(words[i:i + size]) for i in range(0, len(words), size)]
    return chunks[:max_chunks] or [""]


def mean_vector(vecs):
    v = vecs.mean(axis=0)
    return v / max(np.linalg.norm(v), 1e-9)


# -------------------------------------------------------------------- CV


def parse_cv(text):
    """Return (whole CV text, {project name: project text})."""
    projects = {}
    section = None
    current = None
    for line in text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip().lower()
            current = None
        elif line.startswith("### ") and section and "project" in section:
            current = line[4:].strip()
            projects[current] = []
        elif current:
            projects[current].append(line)
    return text, {k: "\n".join([k, *v]).strip() for k, v in projects.items()}


def short_project(name):
    for sep in (" — ", " – ", " - ", ": "):
        if sep in name:
            return name.split(sep)[0].strip()
    return re.sub(r"\s+(System|Platform|Assistant)$", "", name).strip()


# ---------------------------------------------------------------- scorer


class Scorer:
    def __init__(self, cfg=None, cv_text=None, embedder=None, skills=None, log=print):
        self.cfg = cfg or load_yaml("scoring.yaml")
        e = self.cfg["embedding"]
        self.embedder = embedder or Embedder(e["model"], log=log)
        self.skills = skills or Skills()
        cv_text = cv_text if cv_text is not None else fact_texts()
        self.cv_text, self.projects = parse_cv(cv_text)
        self.cv_skills = set(self.skills.find(self.cv_text))
        self._cv_vec = None
        self._proj_vecs = None
        self.target = [re.compile(p, re.I) for p in self.cfg["target_titles"]]
        self.related = [re.compile(p, re.I) for p in self.cfg["related_titles"]]
        self.domain = [re.compile(p, re.I) for p in self.cfg["domain_keywords"]]

    def _doc_vec(self, text):
        e = self.cfg["embedding"]
        return mean_vector(self.embedder.encode(chunk_words(text, e["chunk_words"], e["max_chunks"])))

    def _ensure_cv(self):
        if self._cv_vec is None:
            e = self.cfg["embedding"]
            self._cv_vec = mean_vector(self.embedder.encode(chunk_words(self.cv_text, e["chunk_words"], 12)))
            self._proj_vecs = {name: self._doc_vec(t) for name, t in self.projects.items()}

    def _scale(self, sim):
        e = self.cfg["embedding"]
        lo, hi = (0.0, 0.35) if self.embedder.fallback else (e["floor"], e["ceiling"])
        return float(min(1.0, max(0.0, (sim - lo) / (hi - lo))))

    def role_kind(self, title):
        if any(p.search(title or "") for p in self.target):
            return "target"
        if any(p.search(title or "") for p in self.related):
            return "related"
        return "other"

    def prepare(self, jobs):
        """Embed all job chunks in one batch (fills the cache)."""
        e = self.cfg["embedding"]
        texts = []
        for j in jobs:
            texts += chunk_words(f"{j.title}\n{j.description}", e["chunk_words"], e["max_chunks"])
        self._ensure_cv()
        if texts:
            self.embedder.encode(texts)

    def score(self, job):
        self._ensure_cv()
        w = self.cfg["weights"]
        text = f"{job.title}\n{job.description}"
        jv = self._doc_vec(text)

        cv_sim = float(jv @ self._cv_vec)
        proj = sorted(((float(jv @ v), n) for n, v in self._proj_vecs.items()), reverse=True)
        best_proj = proj[0][0] if proj else 0.0

        job_skills = self.skills.find(text)
        matched = [s for s in job_skills if s in self.cv_skills]
        gaps = [s for s in job_skills if s not in self.cv_skills]
        prior = self.cfg.get("skills_prior_weight", 2)
        skill_score = (len(matched) + 0.5 * prior) / (len(job_skills) + prior)

        level, stretch = detect_level(job.title, job.description)
        level_score = self.cfg["level_scores"].get(level, 0.5)

        kind = self.role_kind(job.title)
        role_score = self.cfg["role_scores"][kind]

        domain_hits = [p.pattern.split("|")[0].strip("\\b") for p in self.domain
                       if p.search(job.title or "") or len(p.findall(job.description or "")) >= 2]
        domain_score = min(1.0, len(domain_hits) / 2)

        parts = {
            "cv_similarity": self._scale(cv_sim),
            "project_similarity": self._scale(best_proj),
            "skills": skill_score,
            "role": role_score,
            "domain": domain_score,
        }
        total_w = sum(w.values()) or 1
        base = sum(w.get(k, 0) * parts[k] for k in parts) / total_w
        parts["level"] = level_score
        fit = round(100 * base * level_score, 1)

        top = [n for s, n in proj[:2] if s > 0]
        why = self._why(kind, level, stretch, top, matched, job_skills, domain_hits)
        return {
            "fit_score": fit,
            "level": level,
            "stretch": stretch,
            "why": why,
            "gaps": gaps,
            "top_projects": top,
            "score_parts": {k: round(v, 3) for k, v in parts.items()} | {"cv_cosine": round(cv_sim, 3)},
        }

    def _why(self, kind, level, stretch, top, matched, job_skills, domain_hits):
        role = {"target": "Target role", "related": "Related role", "other": "Adjacent role"}[kind]
        lvl = "level not stated" if level == "unspecified" else f"{level} level"
        bits = [f"{role}, {lvl}{' (stretch)' if stretch else ''}"]
        if top:
            bits.append("closest projects: " + " and ".join(short_project(t) for t in top))
        if job_skills:
            bits.append(f"{len(matched)}/{len(job_skills)} skills match")
        if domain_hits:
            bits.append("fintech/risk domain")
        return "; ".join(bits)
