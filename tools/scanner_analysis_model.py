"""Step 2.2 analysis model of proposed normative scanner behavior N1 to N4. NOT a scanner.

This model exists only to measure the effect of the proposals on pinned local checkouts before the
operator freezes any normative behavior. It is not wired into any gate, replaces no scanner, changes
no allow-list and is not a security boundary. N5 (hub scanner) is deferred and not modelled; the
production-safe and enterprise-safe wording (S-02) is deferred and deliberately left out of the rule.
Non-authorizing. Standard library only; the lookalike table and the HTML element list are taken from
the pinned scanner modules that the caller supplies.
"""
import html
import re
import unicodedata
from dataclasses import dataclass

SEP = r"[\s\-_]*"
END = r"(?![a-z0-9])"
RULES = {
    "certified": re.compile(r"\bcertif(?:ied|ies|ying|y|ication)\b"),
    "compliant": re.compile(r"\bcompl(?:iant|iance|y|ies|ied|ying)\b"),
    "production-ready": re.compile(
        rf"\b(?:production|prod|deployment|deploy|enterprise|audit){SEP}(?:ready|grade|quality|worthy){END}"
        rf"|\b(?:ready|approved|safe|fit|suitable|cleared){SEP}for{SEP}(?:production|prod|deployment|deploy){END}"
        rf"|\b(?:deployment|deploy){SEP}(?:approved|cleared){END}"
    ),
    "attested": re.compile(
        rf"\bsoc{SEP}[123]\b.{{0,40}}?\battest(?:ed|ation|s)?\b"
        rf"|\battest(?:ed|ation|s)?\b.{{0,40}}?\bsoc{SEP}[123]\b"
        rf"|\bsoc{SEP}[123]\b(?:{SEP}type{SEP}(?:i{{1,2}}|[12]))?{SEP}(?:attest|audit)"
    ),
}
PRE_FOLD = str.maketrans({"ς": "c", "ϲ": "c", "Ϲ": "c"})
EXTRA_DASHES = "−⁃﹣˗⸺⸻－"
ENTITY = re.compile(r"&(?:#[0-9]{1,7}|#[xX][0-9a-fA-F]{1,6}|[A-Za-z][A-Za-z0-9]{1,31});")
COMMENT = re.compile(r"<!--(.*?)-->", re.DOTALL)
MARKS = re.compile(r"[*`~\\]")


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    rule: str
    text: str
    visibility: str  # "visible" or "hidden_comment"


def union_table(*tables):
    out = {}
    for table in tables:
        for key, value in table.items():
            out[ord(key) if isinstance(key, str) else key] = value
    for key in (ord("ς"), ord("ϲ"), ord("Ϲ")):
        out.pop(key, None)  # handled by the pre-fold, before casefold makes them unreachable
    return out


def _invisible(ch):
    cp = ord(ch)
    return unicodedata.category(ch) in {"Cf", "Mn", "Me"} or 0xFE00 <= cp <= 0xFE0F or 0xE0100 <= cp <= 0xE01EF


def _entities(text):
    def one(m):
        out = html.unescape(m.group(0))
        return " " if any(c in out for c in "\r\n\x0b\x0c\x85  ") else out
    return ENTITY.sub(one, text)


ESCAPED_SPACE = re.compile(r"\\[nrt]")  # literal \n, \r, \t in source strings are line and word breaks, not word characters


def normalise(text, table):
    chars, lines, line = [], [], 1
    for raw in unicodedata.normalize("NFKC", ESCAPED_SPACE.sub(" ", _entities(text)).translate(PRE_FOLD)):  # pre-fold first: NFKC maps U+03F9 to a capital sigma
        if raw == "\n":
            line += 1
        for part in unicodedata.normalize("NFD", raw):
            if _invisible(part):
                continue
            for ch in part.casefold():
                if unicodedata.category(ch) == "Pd" or ch in EXTRA_DASHES:
                    ch = "-"
                chars.append(ch.translate(table))
                lines.append(line)
    return "".join(chars), lines


def _drop(norm, lines, spans):
    keep = [True] * len(norm)
    for start, end in spans:
        for i in range(start, end):
            keep[i] = keep[i] and norm[i] == "\n"
    return ("".join(c for c, k in zip(norm, keep) if k), [n for n, k in zip(lines, keep) if k])


def _matches(norm, lines, source, path, visibility, offset_lines=0):
    out = []
    for rule, pattern in RULES.items():
        for m in pattern.finditer(norm):
            ln = lines[m.start()] if m.start() < len(lines) else len(source)
            raw = source[ln - 1] if 0 < ln <= len(source) else ""
            out.append(Finding(path, ln, rule, raw.strip(), visibility))
    return out


def scan_text(path, text, *, table, tag, html_elements):
    """N1 rule union; N2 fold; N3 dual view plus underscore view; N4 comment text scanned separately."""
    norm, lines = normalise(text, table)
    source = unicodedata.normalize("NFKC", text).split("\n")
    comment_spans = [m.span() for m in COMMENT.finditer(norm)]
    mark_spans = [m.span() for m in MARKS.finditer(norm)]
    tag_spans = [m.span() for m in tag.finditer(norm) if m.group(1) in html_elements or "-" in m.group(1)]
    visible = []
    for spans in (comment_spans + mark_spans + tag_spans, comment_spans + mark_spans):  # N3 dual view
        view, view_lines = _drop(norm, lines, spans)
        visible += _matches(view, view_lines, source, path, "visible")
        underscore = [m.span() for m in re.finditer(r"_", view)]  # N3 underscore repair
        view2, lines2 = _drop(view, view_lines, underscore)
        visible += _matches(view2, lines2, source, path, "visible")
    seen = {(f.line, f.rule) for f in visible}
    hidden = []
    for m in COMMENT.finditer(norm):  # N4
        inner = m.group(1)
        base = lines[m.start(1)] if m.start(1) < len(lines) else 1
        inner_lines = lines[m.start(1):m.end(1)]
        for f in _matches(inner, inner_lines, source, path, "hidden_comment"):
            if (f.line, f.rule) not in seen:
                hidden.append(f)
    return sorted(set(visible + hidden), key=lambda f: (f.path, f.line, f.rule, f.visibility))
