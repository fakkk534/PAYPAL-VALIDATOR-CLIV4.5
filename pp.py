#!/usr/bin/env python3

# VERSION  : 4.5
# SCRIPT   : PAYPAL VALIDATOR DETECTED COUNTRY
# WEBSITE  : https://www.darkxcode.pw/
# DOCS     : https://darkxcode.pw/docs/api#paypal-validator
# AUTHOR   : ZLAXTERT
# TELEGRAM : https://t.me/zlaxtert

from __future__ import annotations

import configparser
import json
import os
import re
import signal
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

API_DEFAULT = "https://darkxcode.pw"
KEY_PATTERN = re.compile(r"^dxx_[a-f0-9]{40}$", re.I)
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
VERSION = "4.5"
SCRIPT_DIR = Path(__file__).resolve().parent
SETTINGS_FILE = SCRIPT_DIR / "settings.ini"
RESULT_DIR = SCRIPT_DIR / "result"

# Windows consoles default to cp1252; provider messages may carry symbols.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

if os.name == "nt":
    os.system("")  # enables ANSI escapes in cmd.exe


class C:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    RESET = "\033[0m"


BANNER = f"""{C.GREEN}
\033[0;37m                                                                          \033[0;34m▄▄▄\033[0;34;47m▀▀▀\033[0;34m█\033[0m
\033[0;37m                                                                           \033[0;34m█\033[0;34;47m   \033[0;34m█\033[0;37m \033[0m
\033[0;37m  \033[0;30;44m▀\033[0;37;44m▄▄▄▄▄▄▄\033[0;30;44m▀\033[0;37m     \033[0;34m▄\033[0;34;47m▀▀\033[0;37m▒▀▀▄\033[0;34m█\033[0;37;44m▄▄\033[0;34m▄▄▄\033[0;37m   \033[0;30;44m▀\033[0;37;44m▄\033[0;34m█\033[0;37m   \033[0;34m▄\033[0;37;44m▄\033[0;30;44m▀\033[0;37m     \033[0;30;44m▀\033[0;37;44m▄▄▄▄▄▄▄\033[0;30;44m▀\033[0;37m     \033[0;34m▄\033[0;34;47m▀▀\033[0;37m▒▀▀▄\033[0;34m█\033[0;37;44m▄▄\033[0;34m▄▄▄\033[0;37m  \033[0;34m█\033[0;34;47m ░ \033[0;34m█\033[0;37m \033[0m
\033[0;37m \033[0;34m█\033[0;37;44m█▓█\033[0;34m█▀█\033[0;37;44m█▓█\033[0;34m█\033[0;37m   \033[0;34m█\033[0;34;47m ░ \033[0;34m█\033[0;37m   ░\033[0;37;44m█▓█\033[0;34m█\033[0;37m   \033[0;34m█\033[0;37;44m█▓\033[0;34m█\033[0;37m   \033[0;34m█\033[0;37m█\033[0;37;44m█▄\033[0;34m▄\033[0;37m  \033[0;34m█\033[0;37;44m█▓█\033[0;34m█▀█\033[0;37;44m█▓█\033[0;34m█\033[0;37m   \033[0;34m█\033[0;34;47m ░ \033[0;34m█\033[0;37m   ░\033[0;37;44m█▓█\033[0;34m█\033[0;37m   \033[0;34m█\033[0;34;47m░▒░\033[0;34m█\033[0;37m \033[0m
\033[0;34m█\033[0;37;44m▓▒▓ \033[0;37m   \033[0;37;44m ▓▒▓\033[0;34m█\033[0;37m \033[0;34m█\033[0;34;47m░▒░\033[0;34m█\033[0;37m    \033[0;34m█\033[0;37;44m▓▒▓\033[0;34m█\033[0;37m  \033[0;34m█\033[0;37;44m▓▒▓ \033[0;37m   \033[0;37;44m ▓▒▓\033[0;34m█\033[0;37m \033[0;34m█\033[0;37;44m▓▒▓ \033[0;37m   \033[0;37;44m ▓▒▓\033[0;34m█\033[0;37m \033[0;34m█\033[0;34;47m░▒░\033[0;34m█\033[0;37m    \033[0;34m█\033[0;37;44m▓▒▓\033[0;34m█\033[0;37m   \033[0;34m█\033[0;34;47m▒▓▒\033[0;34m█\033[0;37m \033[0m
\033[0;34m█\033[0;37;44m▒░▒\033[0;34m▓\033[0;37m   \033[0;34m▓\033[0;37;44m▒░▒\033[0;34m█\033[0;37m \033[0;34m█\033[0;34;47m▒▓▒\033[0;34m█\033[0;37m    \033[0;34m█\033[0;37;44m▒░▒\033[0;35;44m░\033[0;37m  \033[0;34m█\033[0;37;44m▒░▒\033[0;34m▓\033[0;37m   \033[0;34m▓\033[0;37;44m▒░▒\033[0;34m█\033[0;37m \033[0;34m█\033[0;37;44m▒░▒\033[0;34m▓\033[0;37m   \033[0;34m▓\033[0;37;44m▒░▒\033[0;34m█\033[0;37m \033[0;34m█\033[0;34;47m▒▓▒\033[0;34m█\033[0;37m    \033[0;34m█\033[0;37;44m▒░▒\033[0;35;44m░\033[0;37m   \033[0;34m█\033[0;34;47m▓█▓\033[0;35;44m░\033[0;37m \033[0m
\033[0;34m█\033[0;37;44m░ ░\033[0;34m▓\033[0;37m   \033[0;34m▓\033[0;37;44m░ ░\033[0;34m█\033[0;37m \033[0;34m█\033[0;34;47m▓█▓\033[0;34m█\033[0;37m    \033[0;34m█\033[0;37;44m░ ░\033[0;35;44m▒\033[0;37m  \033[0;34m█\033[0;37;44m░ ░\033[0;34m▓\033[0;37m   \033[0;34m▓\033[0;37;44m░ ░\033[0;34m█\033[0;37m \033[0;34m█\033[0;37;44m░ ░\033[0;34m▓\033[0;37m   \033[0;34m▓\033[0;37;44m░ ░\033[0;34m█\033[0;37m \033[0;34m█\033[0;34;47m▓█▓\033[0;34m█\033[0;37m    \033[0;34m█\033[0;37;44m░ ░\033[0;35;44m▒\033[0;37m   \033[0;34m█\033[0;34;44m \033[0;94;44m░ \033[0;35;44m▒\033[0;37m \033[0m
\033[0;34m██\033[0;34;44m \033[0;94;44m░▒ \033[0;34m▄\033[0;94;44m ▒░\033[0;34;44m \033[0;34m█\033[0;37m   \033[0;34m█\033[0;94;44m░▒░ \033[0;34m▄\033[0;37m \033[0;35m▄\033[0;34m█\033[0;34;44m \033[0;94;44m░ \033[0;35;44m▓\033[0;37m   \033[0;34m█\033[0;34;44m \033[0;94;44m░▒ \033[0;34m▄\033[0;94;44m ▒░\033[0;34;44m \033[0;34m██\033[0;37m \033[0;34m██\033[0;34;44m \033[0;94;44m░▒ \033[0;34m▄\033[0;94;44m ▒░\033[0;34;44m \033[0;34m█\033[0;37m   \033[0;34m█\033[0;94;44m░▒░ \033[0;34m▄\033[0;37m \033[0;35m▄\033[0;34m█\033[0;34;44m \033[0;94;44m░ \033[0;35;44m▓\033[0;37m   \033[0;34m█\033[0;94;44m░▒░\033[0;35;44m▓\033[0;37m \033[0m
\033[0;34m█\033[0;37;44m░\033[0;34m█\033[0;37;44m░\033[0;35;44m■▄\033[0;35m■\033[0;35;44m▄▄▄\033[0;35m▀\033[0;37m      \033[0;34m▀\033[0;35m▀▀▀▀\033[0;37m  \033[0;35m▀■\033[0;35;44m▄\033[0;35m█▄\033[0;37m   \033[0;35m▀\033[0;35;44m▄▄▄\033[0;35m■\033[0;35;44m▄■\033[0;37;44m░\033[0;34m█\033[0;37;44m░\033[0;34m█\033[0;37m \033[0;34m█\033[0;37;44m░\033[0;34m█\033[0;37;44m░\033[0;35;44m■▄\033[0;35m■\033[0;35;44m▄▄▄\033[0;35m▀\033[0;37m      \033[0;34m▀\033[0;35m▀▀▀▀\033[0;37m  \033[0;35m▀■\033[0;35;44m▄\033[0;35m█▄\033[0;37m  \033[0;34m█\033[0;34;45m▀▀▀ \033[0;37m \033[0m
\033[0;34m█\033[0;37;44m▒\033[0;34m█\033[0;37;44m▒\033[0;34m█\033[0;37m                             \033[0;34m▄▄\033[0;37m  \033[0;34m█\033[0;37;44m▒\033[0;34m█\033[0;37;44m▒\033[0;34m█\033[0;37m \033[0;34m█\033[0;37;44m▒\033[0;34m█\033[0;37;44m▒\033[0;34m█\033[0;37m                         \033[0;34m▀▀\033[0;37m     \033[0m
\033[0;34m█\033[0;37;44m▓▄▓\033[0;34m█\033[0;37m                           \033[0;34m▄\033[0;37;44m▄▀▀▄▄▄▓▄▀\033[0;34m█\033[0;37m \033[0;34m█\033[0;37;44m▓▄▓\033[0;34m█\033[0;37m                                \033[0m
\033[0;34m▀▀▀▀▀\033[0;37m                            \033[0;34m▀\033[0;37m  \033[0;34m▀▀▀▀▀▀\033[0;37m  \033[0;34m▀▀▀▀▀\033[0;37m                                \033[0m

{C.RED}       ==================================================================={C.RESET}
                  |{C.BLUE} SCRIPT{C.RESET}   :{C.GREEN} VALIDATOR PAYPAL DETECT COUNTRY{C.RESET} |
                  |{C.BLUE} VERSION{C.RESET}  :{C.GREEN} {VERSION}{C.RESET}                             |
                  |{C.BLUE} API FROM {C.RESET}:{C.GREEN} https://darkxcode.pw/ {C.RESET}          |
                  |{C.BLUE} AUTHOR   {C.RESET}:{C.GREEN} https://t.me/zlaxtert {C.RESET}          |
{C.RED}       ==================================================================={C.RESET}
"""

COLORS = {
    "LIVE": C.GREEN,
    "DIE": C.RED,
    "RETRY": C.YELLOW,
    "UNKNOWN": C.MAGENTA,
    "ERROR": C.WHITE,
}

VARIANTS = ("LIVE", "DIE", "RETRY", "UNKNOWN", "ERROR")


def ask(label: str) -> str:
    return input(f"{C.RESET}[{C.YELLOW}+{C.RESET}]{C.BLUE} {label}{C.GREEN} >> {C.BLUE}").strip()


def normalize_email(raw: str) -> str | None:
    email = raw.strip()

    if email == "" or len(email) > 254 or EMAIL_PATTERN.match(email) is None:
        return None

    return email


def normalize_proxy(raw: str) -> str | None:
    line = raw.strip()

    if line == "":
        return None

    candidate = line if "://" in line else "http://" + line

    try:
        parts = urllib.parse.urlsplit(candidate)
        port = parts.port
    except ValueError:
        return None

    if parts.hostname is None or port is None or not 1 <= port <= 65535:
        return None

    return candidate


def extract_country(data: dict) -> str:
    """Country label like "(ID) INDONESIA", or '' when the API returned none.

    The API sends the raw name + code under data.info, and a ready-rendered
    label under columns; the label is the fallback for older responses.
    """
    info = (data.get("data") or {}).get("info") or {}
    country = " ".join(str(info.get("country") or "").split()).upper()
    code = str(info.get("country_code") or "").upper()

    if country == "" and code == "":
        return " ".join(str((data.get("columns") or {}).get("country") or "").split())

    if code and country:
        return f"({code}) {country}"

    return country or code


def post_json(url: str, key: str, payload: dict, timeout: int) -> tuple[int, dict]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "X-API-Key": key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace")

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"status": "error", "message": raw[:200]}

        return error.code, parsed if isinstance(parsed, dict) else {}


class RateGate:
    """Serialises request starts so the key stays under its per-second cap."""

    def __init__(self, per_second: int) -> None:
        self.lock = threading.Lock()
        self.interval = 1.0 / per_second
        self.next_at = time.monotonic()

    def wait(self) -> None:
        with self.lock:
            now = time.monotonic()

            if now < self.next_at:
                time.sleep(self.next_at - now)
                now = time.monotonic()

            self.next_at = now + self.interval


class PayPalValidator:
    def __init__(self, api: str, key: str) -> None:
        self.api = api.rstrip("/")
        self.key = key
        self.emails: list[str] = []
        self.proxies: list[str] = []
        self.threads = 2
        self.retries = 3
        self.timeout = 90
        self.out = RESULT_DIR

        self.gate = RateGate(40)
        self.lock = threading.Lock()
        self.proxy_index = 0
        self.counts = {name: 0 for name in VARIANTS}
        self.credit = 0
        self.remaining = 0
        self.done = 0
        self.fatal = ""
        self.stop = False
        self.out.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ API

    def account(self) -> None:
        code, data = post_json(f"{self.api}/api/account/status", self.key, {}, 60)

        if code == 401:
            print(f"{C.YELLOW}[!]{C.RESET}{C.BLUE} {data.get('message', 'Invalid API key.')}{C.RESET}")
            raise SystemExit(1)

        if code != 200:
            print(f"{C.YELLOW}[!]{C.RESET}{C.BLUE} Account status failed (HTTP {code}): "
                  f"{data.get('message', '')}{C.RESET}")
            raise SystemExit(1)

        user = (data.get("user") or {}).get("username", "-")
        subscription = data.get("subscription") or {}
        billing = data.get("billing") or {}
        self.remaining = int(data.get("credits", 0))
        cost = int(billing.get("bounce_cost") or 5)
        free = ", ".join(billing.get("bounce_free_on") or ["RETRY", "UNKNOWN"])

        plan = "subscriber" if subscription.get("active") else "credits"
        print(f"{C.RESET}[{C.YELLOW}+{C.RESET}]{C.BLUE} Account: {C.GREEN}{user}{C.BLUE} | "
              f"credits: {C.GREEN}{self.remaining}{C.BLUE} ({plan}){C.RESET}")
        print(f"{C.RESET}[{C.YELLOW}+{C.RESET}]{C.BLUE} Billing: {C.GREEN}{cost}{C.BLUE} credit(s) per "
              f"LIVE/DIE | free: {C.GREEN}{free}{C.RESET}")

        if self.remaining < cost and not subscription.get("active"):
            print(f"{C.YELLOW}[!]{C.RESET}{C.BLUE} No credits left on this API key{C.RESET}")
            raise SystemExit(1)

    def next_proxy(self) -> str:
        with self.lock:
            proxy = self.proxies[self.proxy_index]
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)

        return proxy

    def save(self, status: str, email: str, country: str, message: str) -> None:
        line = f"{status} | {email} | {country or '-'} | {json.dumps(message)}\n"

        with self.lock:
            with (self.out / f"{status}.txt").open("a", encoding="utf-8") as handle:
                handle.write(line)

    def check_one(self, email: str) -> tuple[str, str, str]:
        """Check one address; returns (status, country, message)."""
        last: tuple[str, str, str] = ("RETRY", "", "no proxy could answer")

        for attempt in range(1, self.retries + 1):
            if self.fatal or self.stop:
                return "ERROR", "", "aborted: " + (self.fatal or "stopped")

            proxy = self.next_proxy()
            self.gate.wait()

            try:
                code, data = post_json(
                    f"{self.api}/api/tools/paypal-validator",
                    self.key,
                    {"input": email, "proxies": [proxy]},
                    self.timeout,
                )
            except (urllib.error.URLError, TimeoutError, OSError) as error:
                last = ("RETRY", "", f"request failed: {error}")
                continue

            message = " ".join(str(data.get("message") or data.get("response") or "").split())

            if code == 429:
                last = ("RETRY", "", "rate limited by API")
                time.sleep(min(5, attempt))
                continue

            if code in (401, 402, 403):
                self.fatal = message or f"HTTP {code}"
                return "ERROR", "", "aborted: " + self.fatal

            if code != 200:
                last = ("RETRY", "", message or f"HTTP {code}")
                continue

            status = str(data.get("status") or "UNKNOWN").upper()

            if status not in COLORS:
                status = "UNKNOWN"

            credit = int(data.get("credit_used") or 0)

            with self.lock:
                self.credit += credit

                if data.get("remaining_credit") is not None:
                    self.remaining = int(data["remaining_credit"])

            if status == "RETRY":
                last = ("RETRY", "", message or "no proxy could answer")
                continue

            return status, extract_country(data), message or status

        return last

    # ------------------------------------------------------------------ flow

    def load_emails(self) -> None:
        path = Path(ask("Enter Email lists file").replace('"', "")).expanduser()

        if not path.is_file():
            print(f"{C.RESET}[{C.YELLOW}!{C.RESET}]{C.BLUE} File {C.GREEN}{path}{C.BLUE} not found "
                  f"{C.RESET}[{C.YELLOW}!{C.RESET}]{C.BLUE}{C.RESET}")
            raise SystemExit(1)

        seen: set[str] = set()

        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                email = normalize_email(line)

                if email is None:
                    if line.strip() != "":
                        print(f"{C.YELLOW}[!]{C.RESET}{C.BLUE} Invalid email: {line.strip()[:60]}{C.RESET}")
                    continue

                key = email.lower()

                if key in seen:
                    continue

                seen.add(key)
                self.emails.append(email)

        if not self.emails:
            print(f"{C.YELLOW}[!]{C.RESET}{C.BLUE} No valid email addresses found{C.RESET}")
            raise SystemExit(1)

        print(f"{C.RESET}[{C.YELLOW}!{C.RESET}]{C.BLUE} Successfully loaded {C.GREEN}{len(self.emails)}"
              f"{C.BLUE} lists from {C.CYAN}{path.name} {C.RESET}[{C.YELLOW}!{C.RESET}]{C.BLUE}{C.RESET}")

    def load_proxies(self) -> None:
        path = Path(ask("Enter Proxy lists file").replace('"', "")).expanduser()

        if not path.is_file():
            print(f"{C.RESET}[{C.YELLOW}!{C.RESET}]{C.BLUE} File {C.GREEN}{path}{C.BLUE} not found "
                  f"{C.RESET}[{C.YELLOW}!{C.RESET}]{C.BLUE}{C.RESET}")
            raise SystemExit(1)

        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                proxy = normalize_proxy(line)

                if proxy is not None and proxy not in self.proxies:
                    self.proxies.append(proxy)

        if not self.proxies:
            print(f"{C.YELLOW}[!]{C.RESET}{C.BLUE} No valid proxies found{C.RESET}")
            raise SystemExit(1)

        print(f"{C.RESET}[{C.YELLOW}!{C.RESET}]{C.BLUE} Successfully loaded {C.GREEN}{len(self.proxies)}"
              f"{C.BLUE} proxies {C.RESET}[{C.YELLOW}!{C.RESET}]{C.BLUE}{C.RESET}")

    def choose_threads(self) -> None:
        raw = ask("Enter number of Threads (2-20) (Recommended 2-10)")

        if raw.isdigit():
            self.threads = max(2, min(20, int(raw)))
        else:
            print(f"{C.YELLOW}[!]{C.RESET}{C.BLUE} Invalid number of threads, using default 2 threads"
                  f" {C.RESET}[{C.YELLOW}!{C.RESET}]{C.BLUE}{C.RESET}")

    def run(self) -> None:
        self.load_emails()
        self.load_proxies()
        self.choose_threads()

        print(f"\n{C.YELLOW}RUNING API FROM {C.GREEN}{self.api}{C.RESET}")
        print(f"{C.YELLOW}USE ENDPOINT {C.GREEN}{self.api}/api/tools/paypal-validator{C.RESET}")
        print(f"{C.RED}={C.RESET}" * 60)
        print(f"{C.YELLOW}Starting validation with {C.GREEN}{self.threads}{C.YELLOW} threads{C.RESET}")
        print(f"{C.RED}={C.RESET}" * 60)

        total = len(self.emails)
        started = time.monotonic()
        executor = ThreadPoolExecutor(max_workers=self.threads)

        try:
            futures = {executor.submit(self.check_one, email): email for email in self.emails}

            for future in as_completed(futures):
                email = futures[future]

                try:
                    status, country, message = future.result()
                except Exception as error:  # a worker bug must not kill the run
                    status, country, message = "ERROR", "", f"worker error: {error}"

                with self.lock:
                    self.done += 1
                    self.counts[status] += 1
                    done = self.done
                    live = self.counts["LIVE"]
                    die = self.counts["DIE"]
                    remaining = self.remaining

                self.save(status, email, country, message)

                paint = COLORS.get(status, C.RESET)
                print(f"{C.YELLOW}Checked{C.RESET} | {C.GREEN}LIVE: {live}{C.RESET} | "
                      f"{C.RED}DIE: {die}{C.RESET} | [{C.RED}{done}{C.RESET}/{C.GREEN}{total}{C.RESET}]"
                      f" - {C.YELLOW}{email}{C.RESET} -> {paint}{status}{C.RESET} | "
                      f"{C.MAGENTA}{country or '-'}{C.RESET} | "
                      f"{C.WHITE}{message[:60]}{C.RESET} | {C.CYAN}CREDIT: {remaining}{C.RESET} | "
                      f"{C.CYAN}BY DARKXCODE V{VERSION}{C.RESET}")

                if self.fatal:
                    print(f"{C.YELLOW}[!]{C.RESET}{C.BLUE} Stopped: {self.fatal}{C.RESET}")
                    break
        finally:
            self.stop = True
            executor.shutdown(wait=True, cancel_futures=True)

        elapsed = time.monotonic() - started
        print()
        print(f"{C.RED}={C.RESET}" * 60)
        print(f"Checking completed! Live: {C.GREEN}{self.counts['LIVE']}{C.RESET} | "
              f"Die: {C.RED}{self.counts['DIE']}{C.RESET}")
        print(f"RETRY: {self.counts['RETRY']} | UNKNOWN: {self.counts['UNKNOWN']} | "
              f"ERROR: {self.counts['ERROR']}")
        print(f"Credits used: {self.credit}")
        print(f"Remaining credit: {self.remaining}")
        print(f"Time taken: {elapsed:.2f} seconds")
        print(f"{C.RESET}[{C.YELLOW}!{C.RESET}]{C.BLUE} Results saved in '{C.GREEN}result{C.BLUE}' folder "
              f"{C.RESET}[{C.YELLOW}!{C.RESET}]{C.BLUE}{C.RESET}")
        print(f"{C.RED}={C.RESET}" * 60)


def load_config() -> tuple[str, str]:
    if not SETTINGS_FILE.exists():
        SETTINGS_FILE.write_text(
            f"[API]\nendpoint = {API_DEFAULT}\n# apikey = dxx_...\n",
            encoding="utf-8",
        )

    config = configparser.ConfigParser()
    config.read(SETTINGS_FILE, encoding="utf-8")
    api = config.get("API", "endpoint", fallback=API_DEFAULT)
    key = os.environ.get("DXX_API_KEY", "").strip() or config.get("API", "apikey", fallback="").strip()

    if key == "":
        key = ask("Enter your API key")

    if KEY_PATTERN.match(key) is None:
        print(f"{C.YELLOW}[!]{C.RESET}{C.BLUE} Invalid API key format (dxx_ + 40 hex){C.RESET}")
        raise SystemExit(1)

    return api, key


def main() -> int:
    print(BANNER)

    def bye(_signum, _frame):
        print(f"\n{C.YELLOW}[!]{C.RESET}{C.BLUE}. . . Exiting . . .{C.RESET}\n")
        raise SystemExit(130)

    try:
        signal.signal(signal.SIGINT, bye)
    except (ValueError, OSError):
        pass

    try:
        api, key = load_config()
        checker = PayPalValidator(api, key)
        checker.account()
        checker.run()
    except (KeyboardInterrupt, EOFError):
        print(f"\n{C.YELLOW}[!]{C.RESET}{C.BLUE}. . . Exiting . . .{C.RESET}\n")
        return 130

    return 0


if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    sys.exit(main())
