from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urldefrag, urljoin, urlsplit
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from rich import box
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.prompt import Confirm, FloatPrompt, IntPrompt, Prompt
from rich.table import Table
from rich.text import Text
from urllib3.util.retry import Retry

APP_NAME = "PitScrapy"
VERSION = "2.0.0"
USER_AGENT = f"PitScrapy/{VERSION} (+https://github.com/devpit/pitscrapy)"
CHUNK_SIZE = 64 * 1024
ROBOTS_MAX_BYTES = 512 * 1024
OUTPUT_NAMES = (
    "links",
    "images",
    "videos",
    "external_scripts",
    "inline_scripts",
    "stylesheets",
    "iframes",
    "emails",
    "phones",
    "forms",
    "headings",
    "meta_tags",
)

console = Console()


class ScraperError(Exception):
    """An expected error that should be displayed without a traceback."""


@dataclass
class Settings:
    output_dir: Path = Path("pitscrapy_results")
    timeout: float = 15.0
    max_size_mb: int = 10
    save: bool = True
    respect_robots: bool = False

    @property
    def max_bytes(self) -> int:
        return self.max_size_mb * 1024 * 1024


@dataclass
class ScrapeResult:
    requested_url: str
    final_url: str
    status_code: int
    content_type: str
    html: bytes = field(repr=False)
    title: str = "Untitled page"
    description: str = ""
    canonical_url: str = ""
    data: dict[str, list[str]] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "requested_url": self.requested_url,
            "final_url": self.final_url,
            "status_code": self.status_code,
            "content_type": self.content_type,
            "bytes_downloaded": len(self.html),
            "title": self.title,
            "description": self.description,
            "canonical_url": self.canonical_url,
            "counts": {key: len(values) for key, values in self.data.items()},
            "data": self.data,
        }


def normalize_target(raw_url: str) -> str:
    """Accept a bare domain, but reject unsupported or ambiguous URL forms."""
    value = raw_url.strip()
    if not value:
        raise ScraperError("A URL is required.")
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", value) and not value.startswith("//"):
        value = f"https://{value}"
    try:
        parsed = urlsplit(value)
        _ = parsed.port 
        if (
            parsed.scheme.lower() not in ("http", "https")
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or any(character.isspace() for character in parsed.netloc)
        ):
            raise ValueError("unsupported or malformed URL")
    except ValueError as exc:
        raise ScraperError("Enter a valid HTTP or HTTPS URL without credentials.") from exc
    return urldefrag(value).url


def absolute_http_url(value: str | None, base_url: str) -> str | None:
    """Resolve relative assets and exclude javascript:, data:, mailto:, etc."""
    if not value or not value.strip():
        return None
    candidate = urljoin(base_url, value.strip())
    try:
        parsed = urlsplit(candidate)
        if parsed.scheme.lower() not in ("http", "https") or not parsed.hostname:
            return None
    except ValueError:
        return None
    return urldefrag(candidate).url


def unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.7",
    })
    retry_policy = Retry(
        total=2,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry_policy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def read_bounded_response(response: requests.Response, max_bytes: int) -> bytes:
    """Read in chunks so a very large response cannot consume unlimited memory."""
    try:
        declared = int(response.headers.get("Content-Length", "0"))
    except ValueError:
        declared = 0
    if declared > max_bytes:
        raise ScraperError(f"Response exceeds the {max_bytes / 1024**2:g} MB size limit.")
    data = bytearray()
    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
        if not chunk:
            continue
        if len(data) + len(chunk) > max_bytes:
            raise ScraperError(f"Response exceeds the {max_bytes / 1024**2:g} MB size limit.")
        data.extend(chunk)
    return bytes(data)


def check_robots(url: str, session: requests.Session, timeout: float) -> None:
    """Check robots.txt when explicitly enabled. Never disguise a denial."""
    parsed = urlsplit(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        with session.get(robots_url, timeout=timeout, stream=True) as response:
            if response.status_code in (401, 403):
                raise ScraperError("Access denied by robots.txt (HTTP 401/403).")
            if response.status_code in (404, 410):
                return
            if response.status_code >= 400:
                raise ScraperError(
                    f"Cannot verify robots.txt (HTTP {response.status_code}). "
                    "Use --no-robots only if you have permission to access this page."
                )
            content = read_bounded_response(response, ROBOTS_MAX_BYTES)
    except RequestException as exc:
        raise ScraperError(f"Unable to check robots.txt: {exc}") from exc
    parser = RobotFileParser()
    parser.parse(content.decode("utf-8-sig", errors="replace").splitlines())
    if not parser.can_fetch(USER_AGENT, url):
        raise ScraperError("This page is disallowed by robots.txt for the current user agent.")


def fetch_html(url: str, session: requests.Session, settings: Settings) -> tuple[bytes, str, int, str]:
    try:
        with session.get(
            url,
            timeout=settings.timeout,
            stream=True,
            allow_redirects=True,
        ) as response:
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
            if content_type and content_type not in ("text/html", "application/xhtml+xml"):
                raise ScraperError(
                    f"Unsupported content type: {content_type}. This tool extracts HTML pages."
                )
            html = read_bounded_response(response, settings.max_bytes)
            final_url = response.url
            status_code = response.status_code
    except RequestException as exc:
        raise ScraperError(f"Request failed: {exc}") from exc
    if not html:
        raise ScraperError("The server returned an empty response.")
    return html, final_url, status_code, content_type


def extract_page(requested_url: str, final_url: str, status_code: int,
                 content_type: str, html: bytes) -> ScrapeResult:
    soup = BeautifulSoup(html, "html.parser")
    base = soup.find("base", href=True)
    base_url = absolute_http_url(base.get("href"), final_url) if base else None
    base_url = base_url or final_url

    def collect_urls(tags: Any, attribute: str = "src") -> list[str]:
        urls: list[str] = []
        for tag in tags:
            resolved = absolute_http_url(tag.get(attribute), base_url)
            if resolved:
                urls.append(resolved)
        return unique(urls)

    links = collect_urls(soup.select("a[href]"), "href")
    images: list[str] = []
    for img in soup.select("img"):
        for attr in ("src", "data-src", "data-lazy-src"):
            resolved = absolute_http_url(img.get(attr), base_url)
            if resolved:
                images.append(resolved)
        srcset = img.get("srcset", "")
        for part in srcset.split(","):
            candidate = part.strip().split(" ", 1)[0]
            resolved = absolute_http_url(candidate, base_url)
            if resolved:
                images.append(resolved)
    images = unique(images)

    videos = collect_urls(soup.select("video[src], video source[src]"))
    external_scripts = collect_urls(soup.select("script[src]"))
    inline_scripts = unique([
        code for tag in soup.select("script:not([src])")
        if (code := tag.get_text(strip=True))
    ])
    stylesheets = collect_urls(
        [tag for tag in soup.select("link[href]")
         if "stylesheet" in [rel.lower() for rel in tag.get("rel", [])]],
        "href",
    )
    iframes = collect_urls(soup.select("iframe[src]"))
    emails = unique([
        tag.get("href", "").partition(":")[2].split("?", 1)[0]
        for tag in soup.select('a[href^="mailto:"]')
        if tag.get("href", "").partition(":")[2]
    ])
    phones = unique([
        tag.get("href", "").partition(":")[2]
        for tag in soup.select('a[href^="tel:"]')
        if tag.get("href", "").partition(":")[2]
    ])
    forms = unique([
        f"{(tag.get('method') or 'GET').upper()} "
        f"{absolute_http_url(tag.get('action') or final_url, base_url) or final_url}"
        for tag in soup.select("form")
    ])
    headings = unique([
        f"{tag.name.upper()} | {' '.join(tag.stripped_strings)}"
        for tag in soup.select("h1, h2, h3") if tag.get_text(strip=True)
    ])
    meta_tags = unique([
        f"{tag.get('name') or tag.get('property') or tag.get('http-equiv')}: {tag.get('content')}"
        for tag in soup.select("meta[content]")
        if tag.get("name") or tag.get("property") or tag.get("http-equiv")
    ])
    description_tag = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
    description = description_tag.get("content", "").strip() if description_tag else ""
    canonical = soup.find("link", rel=lambda value: value and "canonical" in value)
    canonical_url = absolute_http_url(canonical.get("href"), base_url) if canonical else None
    title = soup.title.get_text(" ", strip=True) if soup.title else ""

    data = dict(zip(OUTPUT_NAMES, (
        links, images, videos, external_scripts, inline_scripts,
        stylesheets, iframes, emails, phones, forms, headings, meta_tags,
    )))
    return ScrapeResult(
        requested_url=requested_url,
        final_url=final_url,
        status_code=status_code,
        content_type=content_type,
        html=html,
        title=title or "Untitled page",
        description=description,
        canonical_url=canonical_url or "",
        data=data,
    )


def scrape(url: str, session: requests.Session, settings: Settings) -> ScrapeResult:
    target = normalize_target(url)
    if settings.respect_robots:
        with console.status("[cyan]Checking robots.txt...[/cyan]", spinner="dots"):
            check_robots(target, session, settings.timeout)
    with console.status("[cyan]Fetching and analyzing HTML...[/cyan]", spinner="dots"):
        html, final_url, status_code, content_type = fetch_html(target, session, settings)
        result = extract_page(target, final_url, status_code, content_type, html)
    return result


def save_result(result: ScrapeResult, root: Path) -> Path:
    host = urlsplit(result.final_url).hostname or "website"
    clean_host = re.sub(r"[^a-zA-Z0-9._-]+", "_", host)[:75]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%fZ")
    folder = root / f"{clean_host}_{stamp}"
    try:
        folder.mkdir(parents=True, exist_ok=False)
        (folder / "source_code.html").write_bytes(result.html)
        (folder / "results.json").write_text(
            json.dumps(result.as_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        for name, values in result.data.items():
            if not values:
                continue
            if name == "inline_scripts":
                content = "\n\n".join(
                    f"// Inline script {index}\n{script}"
                    for index, script in enumerate(values, start=1)
                ) + "\n"
                (folder / "inline_scripts.js").write_text(content, encoding="utf-8")
            else:
                (folder / f"{name}.txt").write_text(
                    "\n".join(values) + "\n", encoding="utf-8"
                )
    except OSError as exc:
        raise ScraperError(f"Unable to save the scan: {exc}") from exc
    return folder


BANNER_ART = (
    "██████  ██ ████████ ███████  ██████ ██████   █████  ██████  ██    ██",
    "██   ██ ██    ██    ██      ██      ██   ██ ██   ██ ██   ██  ██  ██",
    "██████  ██    ██    ███████ ██      ██████  ███████ ██████    ████",
    "██      ██    ██         ██ ██      ██   ██ ██   ██ ██         ██",
    "██      ██    ██    ███████  ██████ ██   ██ ██   ██ ██         ██",
)
BANNER_GREEN = "#13A10E"
AUTHOR = "Developed by Pit"
PROJECT_URL = "https://github.com/devpit/pitscrapy"


def show_banner(target_console: Console | None = None) -> None:
    """Show the green pixel-style project logo and original attribution."""
    output = target_console if target_console is not None else console
    if output.width >= max(map(len, BANNER_ART)):
        logo = "\n".join(BANNER_ART)
    else:
        logo = "PITSCRAPY"

    banner = Text(logo, style=BANNER_GREEN, no_wrap=True)
    banner.append(f"\n{AUTHOR}\n{PROJECT_URL}", style=BANNER_GREEN)
    output.print()
    output.print(banner, overflow="ignore", no_wrap=True, crop=False)
    output.print()


def show_summary(result: ScrapeResult, folder: Path | None) -> None:
    details = Table.grid(padding=(0, 2))
    details.add_column(style="bold cyan", no_wrap=True)
    details.add_column(overflow="fold")
    details.add_row("Title", result.title)
    details.add_row("URL", result.final_url)
    details.add_row("HTTP status", f"[green]{result.status_code} OK[/green]")
    details.add_row("HTML size", f"{len(result.html):,} bytes")
    if result.description:
        details.add_row("Description", result.description[:200])
    if folder:
        details.add_row("Saved to", str(folder.resolve()))
    else:
        details.add_row("Saved to", "Not saved")
    console.print(Panel(details, title="[bold green]Scan completed[/bold green]", border_style="green"))

    table = Table(title="Discovered resources", box=box.ROUNDED, header_style="bold cyan")
    table.add_column("Category", style="white", min_width=19)
    table.add_column("Count", justify="right", style="bold green")
    for name in OUTPUT_NAMES:
        count = len(result.data.get(name, []))
        table.add_row(name.replace("_", " ").title(), str(count))
    console.print(table)


def show_preview(result: ScrapeResult, name: str, limit: int = 8) -> None:
    entries = result.data.get(name, [])
    if not entries:
        console.print(f"[yellow]No {escape(name.replace('_', ' '))} found.[/yellow]")
        return
    table = Table(
        title=f"{name.replace('_', ' ').title()} — showing {min(limit, len(entries))} of {len(entries)}",
        box=box.SIMPLE_HEAVY, show_lines=False,
    )
    table.add_column("#", width=4, style="dim", justify="right")
    table.add_column("Value", overflow="fold")
    for index, value in enumerate(entries[:limit], start=1):
        preview = value if len(value) <= 350 else value[:347] + "..."
        table.add_row(str(index), escape(preview))
    console.print(table)


def run_scan(raw_url: str, session: requests.Session, settings: Settings) -> ScrapeResult | None:
    try:
        result = scrape(raw_url, session, settings)
        saved_folder = save_result(result, settings.output_dir) if settings.save else None
    except ScraperError as exc:
        console.print(Panel(escape(str(exc)), title="[bold red]Scan failed[/bold red]", border_style="red"))
        return None
    show_summary(result, saved_folder)
    for category in ("links", "images", "videos", "external_scripts"):
        if result.data[category]:
            show_preview(result, category, limit=5)
    return result


def configure(settings: Settings) -> None:
    console.print(Panel("Adjust scan settings. Press Enter to keep the current value.", title="Settings"))
    settings.timeout = FloatPrompt.ask("Request timeout (seconds)", default=settings.timeout)
    if settings.timeout <= 0:
        console.print("[yellow]Timeout must be positive; using 15 seconds.[/yellow]")
        settings.timeout = 15.0
    settings.max_size_mb = IntPrompt.ask("Maximum HTML size (MB)", default=settings.max_size_mb)
    if settings.max_size_mb <= 0:
        console.print("[yellow]Size must be positive; using 10 MB.[/yellow]")
        settings.max_size_mb = 10
    settings.output_dir = Path(Prompt.ask("Output directory", default=str(settings.output_dir))).expanduser()
    settings.save = Confirm.ask("Save results to disk?", default=settings.save)
    settings.respect_robots = Confirm.ask("Check robots.txt before each scan?", default=settings.respect_robots)
    console.print("[green]Settings updated.[/green]")


def interactive(session: requests.Session, settings: Settings) -> int:
    last: ScrapeResult | None = None
    while True:
        console.print("\n[bold cyan]MAIN MENU[/bold cyan]  [1] Scan URL   [2] Browse last scan   [3] Settings   [4] Exit")
        choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4"], default="1")
        if choice == "1":
            url = Prompt.ask("Website URL (https:// optional)").strip()
            scanned = run_scan(url, session, settings)
            if scanned:
                last = scanned
        elif choice == "2":
            if last is None:
                console.print("[yellow]No successful scans yet.[/yellow]")
                continue
            populated = [(str(idx), name) for idx, name in enumerate(OUTPUT_NAMES, 1) if last.data[name]]
            if not populated:
                console.print("[yellow]The last scan contained no resources.[/yellow]")
                continue
            for idx, name in populated:
                console.print(f"  [cyan]{idx:>2}[/cyan]  {name.replace('_', ' ').title()} ({len(last.data[name])})")
            choices = [idx for idx, _ in populated] + ["0"]
            selected = Prompt.ask("Category number (0 to cancel)", choices=choices, default="0")
            if selected != "0":
                show_preview(last, OUTPUT_NAMES[int(selected) - 1], limit=25)
        elif choice == "3":
            configure(settings)
        else:
            console.print("[dim]Goodbye![/dim]")
            return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="pitscrapy",
        description="Interactive HTML scraper with Rich terminal UI and structured exports.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-u", "--url", help="Scan a website once and exit. Omit for interactive mode.")
    parser.add_argument("-o", "--output", type=Path, default=Path("pitscrapy_results"), help="Results directory.")
    parser.add_argument("--timeout", type=float, default=15.0, help="Request timeout in seconds.")
    parser.add_argument("--max-size-mb", type=int, default=10, help="Maximum HTML response size in MB.")
    parser.add_argument("--no-save", action="store_true", help="Print results without saving files.")
    robots_group = parser.add_mutually_exclusive_group()
    robots_group.add_argument("--respect-robots", action="store_true", help="Check robots.txt before requesting a page.")
    robots_group.add_argument("--no-robots", action="store_true", help="Skip robots.txt checks (default).")
    parser.add_argument("--version", action="version", version=f"{APP_NAME} {VERSION}")
    args = parser.parse_args(argv)
    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero")
    if args.max_size_mb <= 0:
        parser.error("--max-size-mb must be greater than zero")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    settings = Settings(
        output_dir=args.output.expanduser(),
        timeout=args.timeout,
        max_size_mb=args.max_size_mb,
        save=not args.no_save,
        respect_robots=args.respect_robots,
    )
    try:
        show_banner()
        with build_session() as session:
            if args.url:
                return 0 if run_scan(args.url, session, settings) else 1
            return interactive(session, settings)
    except (KeyboardInterrupt, EOFError):
        console.print("\n[yellow]Cancelled by user.[/yellow]")
        return 130


if __name__ == "__main__":
    sys.exit(main())
