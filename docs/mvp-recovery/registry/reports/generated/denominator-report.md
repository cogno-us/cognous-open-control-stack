# Denominator Report

Informational only. Non-authorizing; authority none; activates nothing; no rule, scenario or test was executed; release and production remain on HOLD.

Catalogue manifest: `sha256:25132e5ce4f0d83e682e96a8e5718634ed849f9d08dc7f1f64506e4a3d44a539` (registry 0.1.0, synthetic sample)

Source revisions:
- SYN1: example/synthetic-source@0000000000000000000000000000000000000000; 16 raw records; inventory `sha256:34fa0773397cccbfd7b2e3f21aebec177162808b2cab51775517671986147168`
- SYN2: example/synthetic-source@0000000000000000000000000000000000000000; 5 raw records; inventory `sha256:68c3606773266b7a98114c0c025f31e22e8355c870c79fa7b6a7a5222176f4fc`

```json
{
 "authority": "none",
 "denominators": {
  "10_historical_verdicts_verbatim": {
   "(none recorded)": 1,
   "FAIL": 1
  },
  "1_canonical_rules_by_normative_type": {
   "advisory": 1,
   "mandatory": 1,
   "reason_code_or_refusal_vocabulary": 1
  },
  "2_logical_governance_scenarios": 2,
  "3_suite_level_acceptance_scenarios": 1,
  "4_adversarial_ideas_or_unexecuted_specifications": 1,
  "5_test_implementations": 1,
  "6_parametrized_test_instances": 2,
  "7_fixtures_and_input_vectors": 3,
  "8_historical_execution_records": 2,
  "9_distinct_execution_identities": 1
 },
 "evidence_kinds": {
  "run_result": 1,
  "validation_claim": 1
 },
 "headline_scenario_count": "none by design: scenario denominators are reported separately and never combined",
 "non_authorizing": true,
 "reason_codes_and_vocabularies_are_not_counted_as_normative_obligations": 1,
 "release_scope_by_layer": {
  "fixtures": {
   "v0_1": 3
  },
  "rules": {
   "v0_1": 3
  },
  "scenarios": {
   "v0_1": 5
  },
  "tests": {
   "v0_1": 1
  }
 },
 "scenario_classes_reported_separately": {
  "adversarial_or_unexecuted_spec": 1,
  "fixture_defined_case": 1,
  "logical": 2,
  "suite_level_acceptance": 1
 },
 "unresolved_accounting": {
  "crosswalk_unresolved_rows": 1,
  "entries_with_unrecorded_source_revision": 0,
  "entries_with_unresolved_mvp_applicability": 7,
  "evidence_unrecorded_source_revisions": 0,
  "unresolved_reference_placeholders": 1,
  "unresolved_relationships": 1
 }
}
```
