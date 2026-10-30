"""Parsers + prefilter, run against the fixtures in their native ATS shapes.

No network, no API key. This is the suite that catches the two bugs that cost
me an evening each: Lever's epoch-milliseconds timestamps, and a bare `sde`
regex that silently matches nothing.
"""
from __future__ import annotations

import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jobhunt import mock
from jobhunt.fetch import parse_ashby, parse_greenhouse, parse_lever, strip_html
from jobhunt.mock import fetch_all_mock

CONFIG = yaml.safe_load((Path(__file__).resolve().parent.parent / "config.yaml")
                        .read_text(encoding="utf-8"))
FILTERS = CONFIG["filters"]


# ------------------------------------------------------------- strip_html ---

def test_strip_html_unescapes_twice():
    """Greenhouse ships HTML-entity-escaped HTML: unescape, strip, unescape."""
    raw = "&lt;p&gt;Go &amp;amp; Java&lt;/p&gt;"
    assert strip_html(raw) == "Go & Java"


def test_strip_html_turns_block_tags_into_newlines():
    out = strip_html("<p>One</p><p>Two</p><ul><li>a</li><li>b</li></ul>")
    assert "One" in out and "Two" in out and "a" in out and "b" in out
    assert "<" not in out


def test_strip_html_handles_none_and_empty():
    assert strip_html(None) == ""
    assert strip_html("") == ""


# ---------------------------------------------------------------- parsers ---

def test_greenhouse_maps_every_field():
    jobs = parse_greenhouse("acme-edge", "Acme Edge", mock.GREENHOUSE["acme-edge"])
    j = next(j for j in jobs if j.title.startswith("Software Engineer II"))
    assert j.job_id == "greenhouse:acme-edge:5501001"
    assert j.ats == "greenhouse"
    assert j.company == "Acme Edge"
    assert j.location == "Bangalore, India"
    assert j.url.startswith("https://boards.greenhouse.io/")
    assert "distributed services" in j.description


def test_lever_concatenates_description_lists_and_additional():
    """The requirements live in lists[], not descriptionPlain. Drop the
    concatenation and every Lever job looks unqualified."""
    jobs = parse_lever("quantstack", "QuantStack", mock.LEVER["quantstack"])
    j = next(j for j in jobs if j.title == "Backend Engineer (Go)")
    assert "market data pipeline" in j.description      # descriptionPlain
    assert "Requirements" in j.description              # lists[].text
    assert "2-5 years backend experience" in j.description  # lists[].content
    assert "No take-home" in j.description              # additionalPlain


def test_lever_createdAt_is_epoch_milliseconds():
    """1.7e12 is milliseconds. Reading it as seconds dates the post to 1970
    and the freshness filter eats the whole board without a word."""
    two_days_ago = (datetime.now(timezone.utc) - timedelta(days=2)).date()
    jobs = parse_lever("quantstack", "QuantStack", mock.LEVER["quantstack"])
    j = next(j for j in jobs if j.title == "Backend Engineer (Go)")
    assert j.posted_at == two_days_ago.isoformat()


def test_ashby_skips_unlisted_drafts():
    jobs = parse_ashby("helioscale", "Helioscale", mock.ASHBY["helioscale"])
    assert all("unlisted" not in j.url for j in jobs)
    assert len(jobs) == 2   # 3 postings, one isListed: false


def test_ashby_reads_compensation_and_html_fallback():
    jobs = parse_ashby("helioscale", "Helioscale", mock.ASHBY["helioscale"])
    networking = next(j for j in jobs if j.title == "Software Engineer, Networking")
    assert networking.salary == "₹32L – ₹48L"
    ds = next(j for j in jobs if j.title == "Data Scientist, Growth")
    assert "Causal inference" in ds.description   # descriptionHtml fallback


def test_job_ids_are_globally_unique_and_namespaced():
    jobs = fetch_all_mock()
    ids = [j.job_id for j in jobs]
    assert len(ids) == len(set(ids))
    assert all(re.match(r"^(greenhouse|lever|ashby):[^:]+:.+$", i) for i in ids)


def test_parsers_take_decoded_json_not_a_response():
    """Parsers are pure: body in, list[Job] out. That is what makes --mock
    exercise the real code path instead of a second implementation."""
    assert parse_greenhouse("x", "X", {}) == []
    assert parse_lever("x", "X", []) == []
    assert parse_ashby("x", "X", {}) == []
