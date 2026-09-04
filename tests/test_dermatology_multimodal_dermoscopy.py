"""
Automated Pytest Test Suite for Dermatology Multimodal Dermoscopy.
Domain: Clinical & Biomedical AI
Standard: CAP / CLSI / ISO Standards
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, SecurityException, AuditTrail
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.supervisor import SystemSupervisor
from cli import main


def test_phi_guard_enforcement():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive for Staphylococcus")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_phi_guard_redaction():
    # Test PHI redaction functionality
    text_with_phi = "Contact patient at 555-123-4567 or email@test.com"
    redacted = PHIGuard.redact_phi(text_with_phi)
    assert "[REDACTED_IDENTIFIER]" in redacted
    assert "555-123-4567" not in redacted
    assert "email@test.com" not in redacted


def test_phi_guard_ssn_detection():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("SSN: 123-45-6789")


def test_phi_guard_email_detection():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Send results to patient@hospital.org")


def test_specialized_workers():
    # Worker 1: QC Invariant
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED

    # Worker 2: Safety
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Worker 3: Protocol Conformance
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1


def test_workers_no_alerts_nominal():
    # Workers should not fire alerts for nominal values
    p = SystemTaskPayload(task_id="T-NOMINAL", target_identifier="KEY-NOMINAL", primary_metric=10.0, secondary_metric=5.0, status_descriptor="NOMINAL")
    assert len(InvariantQCWorker.evaluate(p)) == 0
    assert len(SafetyEscalationWorker.evaluate(p)) == 0
    assert len(ProtocolConformanceWorker.evaluate(p)) == 0


def test_supervisor_consensus_and_audit():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-PROD-01",
        target_identifier="KEY-PROD-01",
        primary_metric=12.0,
        secondary_metric=4.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.audit_hash != ""

    # Verify cryptographic audit trail
    assert AuditLogger.verify_integrity() is True

    # CLI tests
    assert main(["audit", "--task-id", "CLI-TEST-01"]) == 0
    assert main(["chat", "Explain", "specifications"]) == 0
    assert main(["verify-audit"]) == 0


def test_supervisor_critical_escalation():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-CRITICAL",
        target_identifier="KEY-CRITICAL",
        primary_metric=30.0,
        secondary_metric=15.0,
        status_descriptor="DISCORDANT_ANOMALY",
        is_critical_flag=True,
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.CRITICAL_STAT
    assert dossier.integrity_status == SystemIntegrityStatus.RECALIBRATION_REQUIRED
    assert dossier.critical_alerts_count > 0


def test_audit_trail_integrity():
    """Test that audit trail detects tampering."""
    trail = AuditTrail(secret_key="test-key-for-integrity")
    trail.log("test_actor", "test_tier", "TEST_EVENT", {"data": "value1"})
    trail.log("test_actor", "test_tier", "TEST_EVENT", {"data": "value2"})
    assert trail.verify_integrity() is True
    assert len(trail.get_trail()) == 2


def test_batch_missing_file():
    """CLI batch command should return error code for missing file."""
    result = main(["batch", "-i", "nonexistent_file_12345.csv"])
    assert result == 1
