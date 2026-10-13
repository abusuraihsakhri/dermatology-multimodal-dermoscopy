/**
 * Browser-only demonstration of the numeric rules in agents/workers.py.
 * These arbitrary thresholds are not dermatology diagnostic criteria.
 */
export function evaluatePayload(payload) {
  const { task_id, target_identifier, primary_metric, secondary_metric,
    status_descriptor, is_critical_flag } = payload;
  if (![task_id, target_identifier, status_descriptor].every(
    value => typeof value === "string" && value.trim().length > 0 && value.length <= 256
  )) {
    throw new Error("Identifiers and descriptor must be non-empty (maximum 256 characters).");
  }
  if (![primary_metric, secondary_metric].every(
    value => typeof value === "number" && Number.isFinite(value)
  )) {
    throw new Error("Both numeric metrics must be finite numbers.");
  }
  if (typeof is_critical_flag !== "boolean") {
    throw new Error("Critical flag must be true or false.");
  }
  const alerts = [];
  const add = (origin_worker, urgency, summary, technical_details) => {
    alerts.push({ origin_worker, urgency, summary, technical_details });
  };
  if (primary_metric > 25) {
    add("InvariantQCWorker", "ELEVATED_RISK", "Primary metric above example threshold",
      "Primary metric is greater than 25 (a synthetic demonstration threshold).");
  }
  if (is_critical_flag || secondary_metric > 12) {
    add("SafetyEscalationWorker",
      is_critical_flag ? "CRITICAL_STAT_PANIC" : "ELEVATED_RISK",
      "Synthetic escalation condition", "Critical flag was set or secondary metric exceeded 12.");
  }
  if (["DISCORDANT", "ANOMALY", "MUTANT", "VIOLATION", "FAIL", "REJECT"].some(
    keyword => status_descriptor.toUpperCase().includes(keyword)
  )) {
    add("ProtocolConformanceWorker", "ELEVATED_RISK",
      "Descriptor matched example anomaly keywords", "Keyword match; no clinical assessment performed.");
  }
  const critical = alerts.filter(a => a.urgency === "CRITICAL_STAT_PANIC").length;
  const overall = critical ? "CRITICAL_STAT_PANIC" : alerts.length ? "ELEVATED_RISK" : "ROUTINE";
  return {
    demo_only: true,
    task_id,
    target_identifier,
    overall_urgency: overall,
    integrity_status: critical ? "RECALIBRATION_REQUIRED" :
      alerts.length ? "DISCORDANT_ANOMALY" : "VALIDATED_OPTIMAL",
    total_alerts: alerts.length,
    critical_alerts_count: critical,
    alerts,
    audit_hash: null,
    interpretation: "Synthetic rule evaluation only. No images, AI model, clinical triage, or HMAC audit were used."
  };
}

if (typeof document !== "undefined") {
  const form = document.querySelector("#audit-form");
  const output = document.querySelector("#output");
  const status = document.querySelector("#run-status");
  const tasks = document.querySelector("#task-count");
  const count = document.querySelector("#alert-count");
  const download = document.querySelector("#download");
  let latest = null;
  let executed = 0;

  form.addEventListener("submit", event => {
    event.preventDefault();
    try {
      latest = evaluatePayload({
        task_id: document.querySelector("#task-id").value,
        target_identifier: document.querySelector("#target-id").value,
        primary_metric: Number(document.querySelector("#primary").value),
        secondary_metric: Number(document.querySelector("#secondary").value),
        status_descriptor: document.querySelector("#descriptor").value,
        is_critical_flag: document.querySelector("#critical").checked
      });
      if (!document.querySelector("#primary").value.trim() ||
          !document.querySelector("#secondary").value.trim()) {
        throw new Error("Both metric fields are required.");
      }
      output.textContent = JSON.stringify(latest, null, 2);
      status.textContent = "Synthetic rules evaluated locally.";
      status.dataset.kind = "success";
      executed += 1;
      tasks.textContent = String(executed);
      count.textContent = String(latest.total_alerts);
      download.disabled = false;
    } catch (error) {
      latest = null;
      output.textContent = "No valid result.";
      status.textContent = error.message;
      status.dataset.kind = "error";
      download.disabled = true;
    }
  });

  download.addEventListener("click", () => {
    if (!latest) return;
    const url = URL.createObjectURL(new Blob([JSON.stringify(latest, null, 2) + "\n"],
      { type: "application/json" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = "dermoscopy-rule-demo.json";
    link.click();
    URL.revokeObjectURL(url);
  });
}
