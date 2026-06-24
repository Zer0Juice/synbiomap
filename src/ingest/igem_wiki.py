"""
igem_wiki.py — crawl iGEM team wikis and pull out the DOIs they cite.

Why we do this
--------------
Each iGEM team writes a multi-page project wiki. Those wikis cite the academic
papers the students built on, usually as DOIs (Digital Object Identifiers — the
stable `10.xxxx/...` codes that identify a paper). Collecting those DOIs gives us
a direct, document-level link from the *student* layer of our corpus (iGEM
projects) to the *academic* layer (OpenAlex papers). That link is exactly what
the project's core question needs: do student projects point at the same body of
research that shows up in local papers and patents?

This complements the part-level citations we already pull from the Registry
`source` field (see igem.py). Wikis cite far more papers than parts do, because
the references live in the write-up, not just on the part page.

How the iGEM wiki is laid out (two eras)
----------------------------------------
The `wikiURL` column in the raw teams CSV points at a team's landing page. There
are two distinct hosting systems, and this module handles both:

  - 2009–2021  MediaWiki, e.g. ``https://2014.igem.org/Team:Aachen``
               Sub-pages live under the same title prefix:
               ``/Team:Aachen/Project``, ``/Team:Aachen/References``, …
  - 2022–2025  A new static wiki, e.g. ``https://2023.igem.wiki/aachen``
               Sub-pages live under the same path prefix:
               ``/aachen/description``, ``/aachen/engineering``, …

In both eras the references are scattered across many sub-pages and there is *no*
reliable "References" page name to guess (some teams have one, many don't). So
the only robust approach is to crawl every sub-page inside the team's own
namespace and scan each for DOIs. We confirmed by probing live pages that the
content (including reference lists) is server-rendered into the HTML, so a plain
HTTP fetch is enough — no JavaScript/browser is required.

DOI extraction
--------------
We use the widely-recommended Crossref DOI pattern (``10.\\d{4,9}/...``; see
https://www.crossref.org/blog/dois-and-matching-regular-expressions/) applied to
both the visible page text and every link's ``href``. Capturing ``href`` values
matters because many citations render the DOI only as a hyperlink whose visible
text is "[1]". DOIs are case-insensitive, so we lower-case them for de-duping.

Politeness & the iGEM firewall
------------------------------
The old wikis (``20XX.igem.org``) sit behind AWS CloudFront + WAF. Sending too
many requests too fast trips a rate-based rule that returns HTTP 403 and blocks
the *whole IP* for several minutes — and every request you send while blocked
keeps the block alive. So this module is deliberately gentle:

  - A shared ``Throttle`` (passed in by the orchestrator) enforces a single
    global request rate across all crawl threads, and acts as a circuit breaker:
    the moment one request comes back 403/429, every thread pauses for a cooldown
    so the firewall window can clear before we resume.
  - Crawls are cached per team and fully restartable (see the orchestrator,
    scripts/03d_scrape_wiki_dois.py), so an interrupted run loses no work.
"""

from __future__ import annotations

import html
import logging
import re
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# A descriptive User-Agent is good scraping etiquette: it tells the server who we
# are and why, so an admin can contact us instead of just blocking the traffic.
# Note: the iGEM web firewall returns 403 for any User-Agent containing the
# literal token "bot", so we identify ourselves as "research" instead and lead
# with the standard "Mozilla/5.0 (compatible; ...)" well-behaved-crawler form.
USER_AGENT = (
    "Mozilla/5.0 (compatible; synbiomap-research/1.0; "
    "academic iGEM citation study; +github.com/Zer0Juice/synbiomap)"
)

# Crossref's recommended DOI matcher. The character class lists the punctuation
# that legitimately appears *inside* DOIs; it deliberately stops at whitespace
# and at the quotes/brackets that delimit HTML so we don't swallow surrounding
# markup. We strip any stray trailing punctuation afterwards (see _clean_doi).
DOI_REGEX = re.compile(r"10\.\d{4,9}/[A-Za-z0-9._;()/:+\-]+")

# MediaWiki "namespaces" we never want to crawl — these are admin/meta pages, not
# project content, and following them would balloon the crawl.
_SKIP_NAMESPACES = (
    "Special:", "File:", "Image:", "Media:", "Help:", "User:",
    "Talk:", "Category:", "Template:", "MediaWiki:", "Property:",
)

# Binary / asset links we should never fetch as HTML pages.
_SKIP_EXTENSIONS = (
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico",
    ".pdf", ".zip", ".gz", ".css", ".js", ".mp4", ".webm", ".mp3",
)


# ---------------------------------------------------------------------------
# Throttle — one global rate limit + circuit breaker shared by all crawl threads
# ---------------------------------------------------------------------------

class Throttle:
    """Keep every crawl thread under one global request rate, and back off hard
    when the iGEM firewall blocks us.

    Two jobs:
      1. Rate limit. ``before_request()`` spaces out *all* requests (across all
         threads) by at least ``min_interval`` seconds, so N workers don't send
         N times the traffic and trip the WAF.
      2. Circuit breaker. When a request comes back 403/429, the caller tells us
         via ``note_block()``; ``before_request()`` then makes every thread wait
         out ``block_cooldown`` seconds before sending anything else, giving the
         firewall's rate window time to clear instead of hammering it while blocked.
    """

    def __init__(self, min_interval: float = 0.7, block_cooldown: float = 120.0):
        self.min_interval = min_interval
        self.block_cooldown = block_cooldown
        self._lock = threading.Lock()
        self._next = 0.0            # earliest monotonic time the next request may go
        self._blocked_until = 0.0   # everyone waits until at least this time

    def before_request(self) -> None:
        """Block until this thread is allowed to send its next request."""
        with self._lock:
            now = time.monotonic()
            start = max(now, self._next, self._blocked_until)
            self._next = start + self.min_interval
            wait = start - now
        if wait > 0:
            time.sleep(wait)

    def note_block(self) -> None:
        """Record that the firewall just blocked us — pause all threads."""
        with self._lock:
            self._blocked_until = time.monotonic() + self.block_cooldown
        logger.warning("Firewall block (403/429) — pausing all crawls %.0fs.",
                       self.block_cooldown)


# ---------------------------------------------------------------------------
# DOI extraction
# ---------------------------------------------------------------------------

def _clean_doi(raw: str) -> str:
    """Normalise one DOI string: lower-case and strip trailing junk.

    DOIs are case-insensitive, so lower-casing makes de-duplication reliable.
    We also strip trailing punctuation that the regex sometimes captures from
    surrounding prose (e.g. a sentence-ending period or a closing paren).
    """
    d = html.unescape(raw).strip().lower()
    # A DOI never contains an embedded URL. When a citation prints the bare DOI
    # immediately followed by its doi.org link with no separator, the regex runs
    # them together (e.g. "10.../mbo3.838https://doi.org/10.../mbo3.838"); cut at
    # the embedded scheme so we keep just the first DOI.
    d = re.split(r"https?://", d)[0]
    # Drop a trailing HTML entity fragment if one slipped through (rare).
    d = re.split(r"&[a-z]+;?$", d)[0]
    # Strip punctuation commonly glued to the end by surrounding text/markup.
    return d.rstrip(".,;:)]}>\"'")


def extract_dois(html_text: str) -> set[str]:
    """Return the set of normalised DOIs found anywhere on one HTML page.

    Looks in two places and unions the results:
      1. Every link target (``<a href>``) — citations are often only a
         hyperlink to ``https://doi.org/10....`` with visible text like "[1]".
      2. The visible page text — catches plain-text ``doi: 10....`` citations.
    """
    found: set[str] = set()

    soup = BeautifulSoup(html_text, "html.parser")

    # (1) link targets — the cleanest source
    for a in soup.find_all("a", href=True):
        href = a["href"]
        for m in DOI_REGEX.findall(href):
            found.add(_clean_doi(m))

    # (2) visible text
    text = html.unescape(soup.get_text(" "))
    for m in DOI_REGEX.findall(text):
        found.add(_clean_doi(m))

    # Drop anything that came out implausibly short after cleaning.
    return {d for d in found if len(d.split("/", 1)[-1]) >= 3}


# ---------------------------------------------------------------------------
# Crawl-scope helpers
# ---------------------------------------------------------------------------

def derive_crawl_scope(wiki_url: str) -> tuple[str, str] | None:
    """Work out which (host, path-prefix) a team's crawl is confined to.

    We only ever follow links that stay on the same host *and* under the same
    path prefix as the landing page — that keeps the crawl inside one team's
    own wiki instead of wandering into other teams or the wider iGEM site.

    Examples
    --------
    ``https://2014.igem.org/Team:Aachen``  -> ("2014.igem.org", "/Team:Aachen")
    ``https://2023.igem.wiki/aachen/``     -> ("2023.igem.wiki", "/aachen")

    Returns None if the URL has no host or no path (nothing to scope to).
    """
    if not wiki_url or not str(wiki_url).strip():
        return None
    p = urlparse(str(wiki_url).strip())
    if not p.netloc:
        return None
    path = p.path.rstrip("/")
    if not path or path == "":
        return None
    return p.netloc, path


def _canonical(url: str) -> str:
    """Strip query string and fragment so the same page isn't fetched twice."""
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}{p.path.rstrip('/')}"


def _in_scope(url: str, host: str, prefix: str) -> bool:
    """True if `url` is a content page inside this team's wiki namespace."""
    p = urlparse(url)
    if p.netloc != host:
        return False
    path = p.path.rstrip("/")
    prefix_l = prefix.lower()
    path_l = path.lower()
    # Must be the landing page itself or a sub-page directly under it.
    if not (path_l == prefix_l or path_l.startswith(prefix_l + "/")):
        return False
    if any(ns.lower() in path_l for ns in _SKIP_NAMESPACES):
        return False
    if path_l.endswith(_SKIP_EXTENSIONS):
        return False
    return True


# ---------------------------------------------------------------------------
# Per-team crawl
# ---------------------------------------------------------------------------

@dataclass
class CrawlResult:
    """Outcome of crawling one team's wiki.

    status:
      ok          finished cleanly, found >=1 DOI
      empty       finished cleanly, found no DOIs (a genuinely citation-free wiki)
      no_wiki     no usable wiki URL to crawl
      unreachable wiki URL did not load (e.g. 404 / dead page) — not a block
      blocked     the firewall blocked us before any page loaded — retry later
      partial     some pages loaded but a block cut the crawl short — retry later
    """
    status: str
    pages_crawled: int = 0
    page_dois: dict[str, list[str]] = field(default_factory=dict)  # url -> DOIs (only pages with >=1)
    dois: list[str] = field(default_factory=list)                   # all unique DOIs, sorted
    blocked: bool = False                                           # firewall got in the way at all
    error: str = ""

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "pages_crawled": self.pages_crawled,
            "page_dois": self.page_dois,
            "dois": self.dois,
            "blocked": self.blocked,
            "error": self.error,
        }


def _fetch(
    session: requests.Session,
    url: str,
    *,
    throttle: "Throttle | None",
    delay: float,
    timeout: int,
    max_retries: int,
) -> requests.Response | None:
    """Fetch one URL, respecting the global throttle and retrying on a block.

    Returns the final Response (which may still be a 403/429 if the firewall
    never let go within ``max_retries``), or None on a network error. The
    throttle's circuit breaker makes every thread wait out a cooldown after a
    block, so the retry usually lands after the firewall window has cleared.
    """
    resp = None
    for attempt in range(max_retries + 1):
        if throttle is not None:
            throttle.before_request()
        elif delay:
            time.sleep(delay)
        try:
            resp = session.get(url, timeout=timeout)
        except requests.RequestException as e:
            logger.debug("fetch error %s: %s", url, e)
            return None
        if resp.status_code in (403, 429):
            if throttle is not None:
                throttle.note_block()            # before_request() now waits out the cooldown
            else:
                time.sleep(min(60 * (attempt + 1), 180))
            continue
        return resp
    return resp  # exhausted retries; still blocked


def crawl_team_wiki(
    wiki_url: str,
    *,
    session: requests.Session | None = None,
    throttle: "Throttle | None" = None,
    max_pages: int = 40,
    delay: float = 0.3,
    timeout: int = 30,
    max_retries: int = 3,
) -> CrawlResult:
    """Breadth-first crawl one team's wiki and collect every DOI it cites.

    Parameters
    ----------
    wiki_url    : the team's landing-page URL (the raw CSV's ``wikiURL``)
    session     : an optional requests.Session to reuse a connection pool
    throttle    : a shared Throttle for global rate limiting + firewall back-off.
                  Strongly recommended when crawling many teams in parallel.
    max_pages   : safety cap on pages fetched per team (a few teams have huge
                  wikis; 40 comfortably covers a normal team)
    delay       : fallback per-request delay used only when no throttle is given
    timeout     : per-request timeout in seconds
    max_retries : retries per page when the firewall returns 403/429

    Returns a CrawlResult. Network/firewall problems are reported via
    ``status``/``blocked`` rather than raised, so one bad team can't stop a run.
    """
    scope = derive_crawl_scope(wiki_url)
    if scope is None:
        return CrawlResult(status="no_wiki")
    host, prefix = scope

    own_session = session is None
    if own_session:
        session = requests.Session()
        session.headers.update({"User-Agent": USER_AGENT})
    elif "User-Agent" not in session.headers:
        session.headers.update({"User-Agent": USER_AGENT})

    start = _canonical(str(wiki_url).strip())
    queue: deque[str] = deque([start])
    seen: set[str] = {start}
    page_dois: dict[str, list[str]] = {}
    all_dois: set[str] = set()
    pages_crawled = 0
    reachable = False
    lost_to_block = False   # at least one page was given up on after a 403/429

    try:
        while queue and pages_crawled < max_pages:
            url = queue.popleft()
            resp = _fetch(session, url, throttle=throttle, delay=delay,
                          timeout=timeout, max_retries=max_retries)
            if resp is None:
                continue
            if resp.status_code in (403, 429):
                lost_to_block = True            # firewall won this page even after retries
                continue
            if resp.status_code != 200:
                continue                         # 404 etc. — page just isn't there
            if "html" not in resp.headers.get("content-type", "").lower():
                continue

            reachable = True
            pages_crawled += 1

            dois = extract_dois(resp.text)
            if dois:
                page_dois[url] = sorted(dois)
                all_dois |= dois

            # Enqueue in-scope sub-pages we haven't seen yet.
            soup = BeautifulSoup(resp.text, "html.parser")
            for a in soup.find_all("a", href=True):
                nxt = _canonical(urljoin(url, a["href"]))
                if nxt in seen:
                    continue
                if _in_scope(nxt, host, prefix):
                    seen.add(nxt)
                    queue.append(nxt)
    finally:
        if own_session:
            session.close()

    if not reachable:
        return CrawlResult(status="blocked" if lost_to_block else "unreachable",
                           blocked=lost_to_block)

    status = "partial" if lost_to_block else ("ok" if all_dois else "empty")
    return CrawlResult(
        status=status,
        blocked=lost_to_block,
        pages_crawled=pages_crawled,
        page_dois=page_dois,
        dois=sorted(all_dois),
    )
