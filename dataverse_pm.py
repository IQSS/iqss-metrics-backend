"""Daily Dataverse PM counts for IQSS/dataverse-pm#596."""

import csv
from datetime import datetime, timedelta, timezone
from functools import partial
import logging
import os
from pathlib import Path
import tempfile

import requests
from rt.rest1 import Rt


GITHUB_API = "https://api.github.com"
HUB_API = "https://hub.dataverse.org/api/installation"
INSTALLATIONS_URL = "https://iqss.github.io/dataverse-installations/data/data.json"
RT_URL = "https://help.hmdc.harvard.edu/REST/1.0/"
TIMEOUT = 30
FILENAME = "dataverse-pm-metrics.tsv"
GITHUB_QUERIES = {
    "github_open_issues": "is:issue is:open",
    "github_open_prs": "is:pr is:open draft:false",
    "github_new_issues": "is:issue created:{day}",
    "github_new_prs": "is:pr created:{day}",
    "github_closed_issues": "is:issue closed:{day}",
    "github_merged_prs": "is:pr merged:{day}",
    "github_closed_bugs": 'is:issue closed:{day} label:"Type: Bug"',
}
COLUMNS = [
    "date", "hub_record_date", *GITHUB_QUERIES,
    "dataverse_releases", "dataverse_frontend_releases",
    "installations_total", "installations_responding",
    "harvard_collections", "harvard_datasets", "harvard_files", "harvard_downloads",
    "rt_new", "rt_closed",
]


def _get(url, **kwargs):
    response = requests.get(url, timeout=TIMEOUT, **kwargs)
    response.raise_for_status()
    return response


def _utc_timestamp(value):
    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        # Python 3.10's ISO parser rejects Hub fractions with 1, 2, 4, or 5 digits.
        timestamp = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
    # Hub recordDate values omit a timezone; the Hub records UTC timestamps.
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    return timestamp.astimezone(timezone.utc)


def _github_metrics(day):
    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    metrics = {}
    for column, query in GITHUB_QUERIES.items():
        data = _get(
            f"{GITHUB_API}/search/issues",
            headers=headers,
            params={"q": "repo:IQSS/dataverse " + query.format(day=day), "per_page": 1},
        ).json()
        if data["incomplete_results"]:
            raise ValueError(f"Incomplete GitHub search results for {column}")
        metrics[column] = data["total_count"]

    for repo, column in [
        ("dataverse", "dataverse_releases"),
        ("dataverse-frontend", "dataverse_frontend_releases"),
    ]:
        metrics[column] = 0
        url = f"{GITHUB_API}/repos/IQSS/{repo}/releases?per_page=100"
        while url:
            response = _get(url, headers=headers)
            for release in response.json():
                if release["draft"] or release["prerelease"] or not release["published_at"]:
                    continue
                if _utc_timestamp(release["published_at"]).date() == day:
                    metrics[column] += 1
            url = response.links.get("next", {}).get("url")
    return metrics


def _hub_metrics(today):
    sites = _get(HUB_API).json()
    harvard_ids = [
        site["dvHubId"] for site in sites
        if site["hostname"].lower() == "dataverse.harvard.edu"
    ]
    if len(harvard_ids) != 1:
        raise ValueError("Expected exactly one Harvard Dataverse installation in the Hub")

    month_start = today.replace(day=1)
    previous_month = (month_start - timedelta(days=1)).replace(day=1)
    next_month = (month_start + timedelta(days=32)).replace(day=1)
    sites = _get(
        f"{HUB_API}/metrics/monthly",
        params={"fromDate": previous_month.strftime("%Y-%m"),
                "toDate": next_month.strftime("%Y-%m")},
    ).json()
    responding = set()
    harvard_records = []
    for site in sites:
        for record in site["metrics"]:
            record_day = _utc_timestamp(record["recordDate"]).date()
            if month_start <= record_day <= today:
                responding.add(site["dvHubId"])
            if site["dvHubId"] == harvard_ids[0] and previous_month <= record_day <= today:
                harvard_records.append(record)
    if not harvard_records:
        raise ValueError("No Harvard Dataverse Hub observations in the current or previous month")
    latest = max(harvard_records, key=lambda record: _utc_timestamp(record["recordDate"]))
    registry = _get(INSTALLATIONS_URL).json()
    return {
        "hub_record_date": latest["recordDate"],
        "installations_total": len(registry["installations"]),
        "installations_responding": len(responding),
        "harvard_collections": latest["dataverses"],
        "harvard_datasets": latest["localDatasets"],
        "harvard_files": latest["files"],
        "harvard_downloads": latest["downloads"],
    }


def _rt_metrics(day):
    tracker = Rt(RT_URL, os.getenv("RT_USER"), os.getenv("RT_PASSWORD"))
    # python-rt does not expose a timeout argument; scope it to this client's session.
    tracker.session.request = partial(tracker.session.request, timeout=TIMEOUT)
    try:
        if not tracker.login():
            raise RuntimeError("Dataverse PM collector could not log in to RT")
        metrics = {}
        for column, field in [("rt_new", "Created"), ("rt_closed", "Resolved")]:
            query = (f"{field} >= '{day} 00:00:00 UTC' AND "
                     f"{field} < '{day + timedelta(days=1)} 00:00:00 UTC'")
            if field == "Resolved":
                query += " AND Status = 'resolved'"
            tickets = tracker.search(Queue="dataverse_support", raw_query=query, Format="i")
            metrics[column] = len({ticket["id"] for ticket in tickets})
        return metrics
    finally:
        tracker.session.close()


def _write_history(output_dir, row):
    target = Path(output_dir) / FILENAME
    rows = []
    if target.exists():
        with target.open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream, delimiter="\t")
            if reader.fieldnames != COLUMNS:
                raise ValueError(f"Unexpected columns in {FILENAME}; existing history was not changed")
            rows = [old for old in reader if old["date"] != row["date"]]
    rows.append(row)
    rows.sort(key=lambda item: item["date"])

    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="", dir=target.parent,
            prefix=FILENAME + ".", delete=False,
        ) as stream:
            temporary = Path(stream.name)
            writer = csv.DictWriter(stream, fieldnames=COLUMNS, delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return target


def harvest_dataverse_pm(output_dir):
    """Store today's snapshots and yesterday's UTC activity, preserving earlier rows."""
    today = datetime.now(timezone.utc).date()
    day = today - timedelta(days=1)
    logging.info("Collecting Dataverse PM snapshots for %s and activity for %s", today, day)
    row = {"date": today.isoformat()}
    row.update(_github_metrics(day))
    row.update(_hub_metrics(today))
    row.update(_rt_metrics(day))
    for column in COLUMNS[2:]:
        if type(row[column]) is not int or row[column] < 0:
            raise ValueError(f"Invalid Dataverse PM count for {column}: {row[column]!r}")
    return _write_history(output_dir, row)
