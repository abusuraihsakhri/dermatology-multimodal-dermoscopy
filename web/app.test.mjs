import test from "node:test";
import assert from "node:assert/strict";
import { evaluatePayload } from "./app.mjs";

const base = {
  task_id: "SYN-1", target_identifier: "DEMO-1",
  primary_metric: 10, secondary_metric: 4,
  status_descriptor: "NOMINAL", is_critical_flag: false
};
test("nominal synthetic example", () => {
  const result = evaluatePayload(base);
  assert.equal(result.overall_urgency, "ROUTINE");
  assert.equal(result.total_alerts, 0);
  assert.equal(result.audit_hash, null);
  assert.equal(result.demo_only, true);
});
test("threshold boundaries are strict", () => {
  assert.equal(evaluatePayload({ ...base, primary_metric: 25, secondary_metric: 12 }).total_alerts, 0);
  assert.equal(evaluatePayload({ ...base, primary_metric: 25.01 }).total_alerts, 1);
  assert.equal(evaluatePayload({ ...base, secondary_metric: 12.01 }).total_alerts, 1);
});
test("critical flag controls critical urgency", () => {
  const result = evaluatePayload({ ...base, is_critical_flag: true });
  assert.equal(result.overall_urgency, "CRITICAL_STAT_PANIC");
  assert.equal(result.critical_alerts_count, 1);
});
test("keyword alerts do not cause critical urgency", () => {
  const result = evaluatePayload({ ...base, status_descriptor: "DISCORDANT" });
  assert.equal(result.overall_urgency, "ELEVATED_RISK");
  assert.equal(result.total_alerts, 1);
});
test("rejects nonfinite numbers and missing values", () => {
  assert.throws(() => evaluatePayload({ ...base, primary_metric: NaN }));
  assert.throws(() => evaluatePayload({ ...base, secondary_metric: Infinity }));
  assert.throws(() => evaluatePayload({ ...base, task_id: "" }));
});
