#!/usr/bin/env python3

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from urllib import error, request
import xml.etree.ElementTree as ET


QASE_BASE_URL = "https://api.qase.io/v1"
TEST_CASE_IDS = {
    "QaseXUnitShowcase.LoginTests.UserCanLogin": 123,
    "QaseXUnitShowcase.LoginTests.InvalidPassword_ShowsError": 124,
    "QaseXUnitShowcase.CalculatorTests.AdditionTest": 300,
}


def build_headers(token):
    return {
        "Token": token,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def http_json(method, url, token, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, headers=build_headers(token), method=method)
    try:
        with request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"Qase API request failed: {exc.code} {exc.reason}", file=sys.stderr)
        print(body, file=sys.stderr)
        raise


def parse_duration(duration_text):
    if not duration_text:
        return 0.0
    text = duration_text.strip()
    if text.startswith("PT"):
        seconds = 0.0
        time_part = text[2:]
        if time_part.endswith("S"):
            time_part = time_part[:-1]
        if not time_part:
            return 0.0
        pieces = []
        current = ""
        for ch in time_part:
            if ch.isalpha():
                if current:
                    pieces.append((current, ch))
                    current = ""
            else:
                current += ch
        if current:
            pieces.append((current, ""))
        for value, unit in pieces:
            num = float(value)
            if unit in ("H", "h"):
                seconds += num * 3600
            elif unit in ("M", "m"):
                seconds += num * 60
            elif unit in ("S", "s", ""):
                seconds += num
        return seconds
    try:
        return float(duration_text)
    except ValueError:
        return 0.0


def list_trx_results(trx_path):
    root = ET.parse(trx_path).getroot()
    ns = {
        "t": "http://microsoft.com/schemas/VisualStudio/TeamTest/2010",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }
    results = []
    for node in root.findall(".//t:UnitTestResult", ns):
        test_name = node.attrib.get("testName", "")
        outcome = node.attrib.get("outcome", "")
        if not test_name or outcome.lower() in {"notexecuted", "notrun", "skipped"}:
            continue
        duration_text = node.attrib.get("duration", "PT0S")
        stacktrace = ""
        err_info = node.find("t:Output/t:ErrorInfo", ns)
        if err_info is not None:
            stack = err_info.find("t:StackTrace", ns)
            if stack is not None and stack.text:
                stacktrace = stack.text.strip()
        results.append(
            {
                "test_name": test_name,
                "outcome": outcome,
                "duration": parse_duration(duration_text),
                "stacktrace": stacktrace,
            }
        )
    return results


def create_run(project, token, title):
    payload = {
        "title": title,
        "description": f"GitHub Actions run {os.getenv('GITHUB_RUN_ID', 'local')} for {os.getenv('GITHUB_REPOSITORY', 'local')}",
        "environment": os.getenv("GITHUB_REF_NAME", "github-actions"),
        "public": False,
    }
    return http_json("POST", f"{QASE_BASE_URL}/run/{project}", token, payload)


def upload_result(project, token, run_id, case_id, status, time_seconds, stacktrace):
    payload = {
        "case_id": case_id,
        "status": status,
        "time": round(time_seconds, 3),
    }
    if stacktrace:
        payload["stacktrace"] = stacktrace
    if status == "failed":
        payload["comment"] = "Failed in GitHub Actions"
    return http_json("POST", f"{QASE_BASE_URL}/result/{project}/{run_id}", token, payload)


def main():
    parser = argparse.ArgumentParser(description="Upload xUnit TRX results to Qase")
    parser.add_argument("--trx", default="TestResults/test-results.trx", help="Path to the TRX file")
    parser.add_argument("--project", default=os.getenv("QASE_TESTOPS_PROJECT", ""), help="Qase project code")
    parser.add_argument("--token", default=os.getenv("QASE_TESTOPS_API_TOKEN", ""), help="Qase API token")
    parser.add_argument("--dry-run", action="store_true", help="Print payloads without uploading")
    parser.add_argument("--title", default=f"GitHub Actions run {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    args = parser.parse_args()

    if not args.project or not args.token:
        print("QASE_TESTOPS_PROJECT or QASE_TESTOPS_API_TOKEN is missing. Skipping Qase upload.")
        return 0

    trx_path = Path(args.trx)
    if not trx_path.exists():
        print(f"TRX file not found: {trx_path}", file=sys.stderr)
        return 2

    results = list_trx_results(trx_path)
    if not results:
        print(f"No test results found in {trx_path}. Nothing to upload.")
        return 0

    if args.dry_run:
        print(json.dumps({"project": args.project, "results": results}, indent=2))
        return 0

    run_response = create_run(args.project, args.token, args.title)
    run_id = None
    if isinstance(run_response, dict):
        result = run_response.get("result") or run_response.get("data")
        if isinstance(result, dict):
            run_id = result.get("id")

    uploaded = 0
    skipped = 0
    if run_id is None:
        raise RuntimeError("Qase run was not created; cannot attach result payloads.")

    for item in results:
        test_name = item["test_name"]
        case_id = TEST_CASE_IDS.get(test_name)
        if case_id is None:
            skipped += 1
            print(f"Skipping upload for {test_name}: no QaseIds mapping found.")
            continue
        status = "passed" if item["outcome"].lower() == "passed" else "failed"
        upload_result(args.project, args.token, run_id, case_id, status, item["duration"], item["stacktrace"])
        uploaded += 1

    print(f"Uploaded {uploaded} result(s) to Qase project {args.project}. Skipped {skipped} unlinked or ignored tests.")
    if run_id is not None:
        print(f"Qase run id: {run_id}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(f"Qase upload failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
