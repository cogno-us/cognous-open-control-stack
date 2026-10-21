"""Check current architecture links against the selected lock, not history.

Historical reports and explicitly separate candidate manifests are outside this
selected-entry-page check. This performs no network requests or authorization.

Scope: only docs/evidence-index.md, docs/architecture.md and docs/operational-trust-status.md
are checked. Every revision-specific link on them to a locked component is compared with the
lock: tree/blob/commit/commits/raw/blame/archive/compare forms on github.com (http or https, with
or without www.), raw.githubusercontent.com and codeload.github.com, under the current or a
previous repository name (docs/repository-renames.md). Other documents are not covered.
"""
import html
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
# Repository locations before the October 2026 rename (docs/repository-renames.md), lowercase.
# A link that still uses an old name is checked against the current repository's selected revision.
OLD_REPOSITORY_NAMES = {
    'cogno-us/cognous-agent-action-manifest': 'cogno-us/cognous-action-manifest',
    'cogno-us/bitrep': 'cogno-us/cognous-evidence-attestation',
    'cogno-us/the-index': 'cogno-us/cognous-evidence-registry',
    'cogno-us/cognous-agent-control-plane': 'cogno-us/cognous-control-plane',
    'cogno-us/moltbot-safe': 'cogno-us/cognous-execution-runtime',
    'cogno-us/cognous-agent-replay-bundle': 'cogno-us/cognous-replay-bundle',
    'cogno-us/cognous-agent-governance-evidence-pack': 'cogno-us/cognous-governance-evidence-pack',
    'cogno-us/alvorada': 'cogno-us/cognous-governed-exchange',
    'cogno-us/constitutional-governance-for-institutions': 'cogno-us/cognous-institutional-governance',
}
# 4 or more hex characters: a revision longer than 40 (never equal to a selected sha) is still judged.
_HEX = r'[0-9a-fA-F]{4,}(?![0-9A-Za-z])'
# Any GitHub-hosted location of a repository: github.com (with or without scheme, www., http or
# https), raw.githubusercontent.com, codeload.github.com and the api.github.com/repos form.
REPOSITORY_URL = re.compile(
    r'(?:https?:)?(?://)?(?:www\.)?(?P<host>github\.com|raw\.githubusercontent\.com|codeload\.github\.com|api\.github\.com/repos)'
    r'/(?P<owner>[^/\s)>\]"\'`]+)/(?P<repo>[^/\s)>\]"\'`]+)(?P<rest>[^\s)>\]"\'`]*)', re.I)
# Revision positions inside the remainder of the path: a keyword segment followed by a revision
# (tree, blob, commit, commits incl. /pull/N/commits/, raw, blame, archive/<sha>.zip, zipball,
# tarball, compare/<a>...<b>; and the api.github.com forms /git/trees/<sha>, /statuses/<sha>, /find/<sha>,
# /pull/N/files/<sha>), or the segment right after the repository on raw/codeload hosts.
_KEYWORD_REVISION = re.compile(r'/(?:tree|blob|trees|commits?|statuses|find|files|raw|blame|archive|zipball|tarball|zip|tar\.gz|compare)/(' + _HEX[:-len('(?![0-9A-Za-z])')] + r')(?![0-9A-Za-z])', re.I)
_RANGE_REVISION = re.compile(r'(?:^|/|\.\.\.?)(' + _HEX[:-len('(?![0-9A-Za-z])')] + r')(?![0-9A-Za-z])', re.I)
_REF_QUERY = re.compile(r'[?&]ref=(' + _HEX[:-len('(?![0-9A-Za-z])')] + r')(?![0-9A-Za-z])', re.I)
_BARE_REVISION = re.compile(r'^/(' + _HEX[:-len('(?![0-9A-Za-z])')] + r')(?![0-9A-Za-z])', re.I)


def _plausible_revision(value):
    """Abbreviations of 7-40 hex characters are revisions. Shorter ones (4-6) count only when they mix
    digits and letters, so a year, an issue number or a word such as /tree/2026 or /tree/face is not
    read as a commit; an all-digit or all-letter 4-6 character abbreviation is therefore not checked."""
    return len(value) >= 7 or (any(c.isdigit() for c in value) and any(c.isalpha() for c in value))


def _same_revision(linked, selected):
    return selected.lower().startswith(linked.lower())


_HOST_DECORATION = re.compile(
    r'((?:www\.)?(?:github\.com|raw\.githubusercontent\.com|codeload\.github\.com|api\.github\.com))\.*(?::[0-9]*)?(?=/)', re.I)
_KEYWORD_SPACE = re.compile(
    r'(/(?:tree|blob|trees|commits?|statuses|find|files|raw|blame|archive|zipball|tarball|zip|tar\.gz|compare)/)\s+(?=[0-9a-fA-F])', re.I)
_FULL_STOPS = str.maketrans({'\u3002': '.', '\uff61': '.', '\uff0e': '.', '\u2024': '.', '\u2e3c': '.'})
# Decode rounds before a link text is refused as over-encoded rather than passed.
MAX_DECODE_ROUNDS = 32


def _normalise_step(text):
    text = unicodedata.normalize('NFKC', unquote(html.unescape(text))).translate(_FULL_STOPS)
    text = text.replace('\\', '/')
    text = re.sub(r'(?<!:)/{2,}', '/', text)       # doubled slashes inside a path
    text = re.sub(r'(?<=:)/{3,}', '//', text)      # https:///host
    text = _HOST_DECORATION.sub(r'\1', text)       # empty/numeric port and trailing dots
    return _KEYWORD_SPACE.sub(r'\1', text)         # whitespace between keyword and revision


def _normalise_checked(text):
    """(normalised text, fixpoint reached). Decoding repeats until nothing changes; hitting the cap
    is reported, never silently passed."""
    for _ in range(MAX_DECODE_ROUNDS):
        decoded = _normalise_step(text)
        if decoded == text:
            return text, True
        text = decoded
    return text, False


def _normalise(text):
    """NFKC, backslash to slash, collapsed slashes, ideographic full stops, an empty or numeric port
    and trailing dots after a GitHub host, whitespace after a keyword segment, and HTML/percent
    decoding to a fixpoint, so an encoded or decorated link is judged like a plain one."""
    return _normalise_checked(text)[0]


def link_problems(text):
    """Reasons the link text cannot be judged (currently: encoding deeper than the decode cap)."""
    return [] if _normalise_checked(text)[1] else ['link encoding deeper than %d decode rounds' % MAX_DECODE_ROUNDS]


UNDECODABLE = '<refused: link encoding too deep>'


def revision_links(text):
    """(current repository name, linked revision) for every revision-specific GitHub link in text.

    Old repository names are mapped to the current ones; the .git suffix is ignored. Whether a link
    names a locked component is decided by the caller. Offline and non-authorizing."""
    found = []
    normalised, settled = _normalise_checked(text)
    if not settled:
        found.append((UNDECODABLE, UNDECODABLE))
    for match in REPOSITORY_URL.finditer(normalised):
        repo = match.group('repo')
        if repo.lower().endswith('.git'):
            repo = repo[:-4]
        name = (match.group('owner') + '/' + repo).lower()
        name = OLD_REPOSITORY_NAMES.get(name, name)
        rest = match.group('rest')
        revisions = [m.group(1) for m in _KEYWORD_REVISION.finditer(rest)]
        if rest.startswith('/compare/') or '/compare/' in rest:
            tail = rest.split('/compare/', 1)[1]
            revisions += [m.group(1) for m in _RANGE_REVISION.finditer(tail)]
        if match.group('host').lower() != 'github.com' and not match.group('host').lower().startswith('api.'):
            bare = _BARE_REVISION.match(rest)
            if bare:
                revisions.append(bare.group(1))
        revisions += [m.group(1) for m in _REF_QUERY.finditer(rest)]
        for sha in dict.fromkeys(r for r in revisions if _plausible_revision(r)):
            found.append((name, sha))
    return found


def verify(root=ROOT):
    lock=json.loads((root/'component-lock.json').read_text())
    selected={spec['repository']:(spec.get('sha') or spec['accepted_sha'])
              for spec in lock['components'].values()}
    architecture=(root/'docs/architecture.md').read_text()
    current=architecture.split('## Component responsibilities',1)[1].split('\n## ',1)[0]
    checked=0
    for name in ('docs/evidence-index.md','docs/architecture.md','docs/operational-trust-status.md'):
        problems=link_problems((root/name).read_text())
        if problems:
            raise ValueError('Selected link cannot be judged: '+name+' '+problems[0])
    for owner,sha in revision_links(current):
        if owner.lower() not in selected or not _same_revision(sha,selected[owner.lower()]):
            raise ValueError('Selected architecture link differs from lock: '+owner+'@'+sha)
        checked+=1
    if not checked:
        raise ValueError('Selected architecture must retain a revision-specific implementation link')
    # Every revision-specific link to any locked component on the three current entry surfaces
    # (any hex case, full or abbreviated to at least 4 characters, including ?ref=) must match that component's selected revision.
    for name in ('docs/evidence-index.md','docs/architecture.md','docs/operational-trust-status.md'):
        for owner,sha in revision_links((root/name).read_text()):
            if owner.lower() in selected and not _same_revision(sha,selected[owner.lower()]):
                raise ValueError('Selected link differs from lock: '+name+' '+owner+'@'+sha)
    index=(root/'docs/evidence-index.md').read_text()
    if 'https://github.com/cogno-us/cognous-stack-orchestrator/issues/30' in index:
        raise ValueError('Public evidence entry must use the public operational trust status')
    if not re.search(r'\[[^\]]+\]\(operational-trust-status\.md\)',index):
        raise ValueError('Missing public trust status evidence link')
    # Check local navigation on the three current entry surfaces only. Historical
    # reports have independent source scope and are not rewritten by this check.
    for name in ('docs/evidence-index.md','docs/architecture.md','docs/operational-trust-status.md'):
        path=root/name
        for target in re.findall(r'\]\(([^\s)]+)\)',path.read_text()):
            if '://' in target or target.startswith('#'):
                continue
            candidate = path.parent/target.split('#',1)[0]
            if (not candidate.resolve().is_relative_to(root.resolve())
                    or any(part.is_symlink() for part in (candidate, *candidate.parents) if part != root.parent)
                    or not candidate.resolve().exists()):
                raise ValueError('Broken local navigation: '+name+' -> '+target)
    return {'selected_revision_links_checked':checked,'network_checked':False,'authorizing':False}


if __name__=='__main__':
    print(json.dumps(verify(),sort_keys=True))
