"""Regression checks for input validation, CSV parsing, audit integrity, and API errors."""
import csv
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from agents.api import app
from agents.base import AuditTrail, SecurityException
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from cli import main as main_cli, parse_csv_boolean
from derma_vision_ai.cli import main as frontier_cli, parse_csv_boolean as frontier_bool


@pytest.mark.parametrize("parse", [parse_csv_boolean, frontier_bool])
@pytest.mark.parametrize("token,expected", [
    ("False", False), ("0", False), ("No", False),
    ("True", True), ("1", True), ("YES", True), ("", False),
])
def test_csv_boolean_tokens(parse, token, expected):
    assert parse(token) is expected


@pytest.mark.parametrize("parse", [parse_csv_boolean, frontier_bool])
def test_csv_boolean_rejects_ambiguous_tokens(parse):
    with pytest.raises(ValueError):
        parse("maybe")


def test_numeric_metrics_are_finite():
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="T", target_identifier="SYN", primary_metric=float("nan"))
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="T", target_identifier="SYN", primary_metric=1, secondary_metric=float("inf"))


def test_attributes_checked_for_phi():
    supervisor = SystemSupervisor()
    payload = SystemTaskPayload(task_id="T", target_identifier="SYN", primary_metric=1,
                                attributes={"comment": "email patient@example.com"})
    with pytest.raises(SecurityException):
        supervisor.process_task(payload)


def test_crypto_audit_detects_mutation_and_returns_copies():
    audit = AuditTrail(secret_key="deterministic-test-key")
    audit.log("tester", "test", "RUN", {"status": "ok"})
    assert audit.verify_integrity()
    trail = audit.get_trail()
    trail[0]["actor"] = "tampered-copy"
    assert audit.verify_integrity()
    audit.logs[0]["actor"] = "tampered"
    assert not audit.verify_integrity()


@pytest.mark.parametrize("command", [main_cli, frontier_cli])
def test_batch_false_flag_stays_false(tmp_path, command):
    source = tmp_path / "batch.csv"
    target = tmp_path / "results.csv"
    with source.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=[
            "task_id", "target_identifier", "primary_metric",
            "secondary_metric", "status_descriptor", "is_critical_flag"
        ])
        writer.writeheader()
        writer.writerow(dict(task_id="CASE-1", target_identifier="DEMO-1",
                             primary_metric=10, secondary_metric=4,
                             status_descriptor="NOMINAL", is_critical_flag="False"))
    assert command(["batch", "-i", str(source), "-o", str(target)]) == 0
    with target.open(newline="", encoding="utf-8") as fp:
        result = next(csv.DictReader(fp))
    assert result.get("overall_urgency", result.get("overall_status")) in (
        "ROUTINE", "NOMINAL_OPTIMAL"
    )


@pytest.mark.parametrize("command", [main_cli, frontier_cli])
def test_bad_batch_does_not_write_output(tmp_path, command):
    source = tmp_path / "batch.csv"
    target = tmp_path / "results.csv"
    source.write_text(
        "task_id,target_identifier,primary_metric,is_critical_flag\n"
        "CASE-1,DEMO-1,10,maybe\n", encoding="utf-8"
    )
    assert command(["batch", "-i", str(source), "-o", str(target)]) == 1
    assert not target.exists()


def test_api_rejects_phi_without_repeating_input():
    client = TestClient(app)
    response = client.post("/api/audit", json={
        "task_id": "CASE", "target_identifier": "SYN",
        "primary_metric": 1, "attributes": {"email": "patient@example.com"}
    })
    assert response.status_code == 422
    assert "patient@example.com" not in response.text
    assert client.get("/health").status_code == 200
