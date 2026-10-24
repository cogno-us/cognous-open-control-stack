# Catalogue Integrity Report

Informational only. Non-authorizing; authority none; activates nothing; no rule, scenario or test was executed; release and production remain on HOLD.

Catalogue manifest: `sha256:3ec81385912077d8e401e4d5690e090930caa7ad15754dc5c0a85bcd58842732` (registry 0.1.0, synthetic sample)

Source revisions:
- SYN1: example/synthetic-source@0000000000000000000000000000000000000000; 16 raw records; inventory `sha256:34fa0773397cccbfd7b2e3f21aebec177162808b2cab51775517671986147168`
- SYN2: example/synthetic-source@0000000000000000000000000000000000000000; 5 raw records; inventory `sha256:68c3606773266b7a98114c0c025f31e22e8355c870c79fa7b6a7a5222176f4fc`

```json
{
 "authority": "none",
 "by_layer": {
  "fixtures": {
   "canonical": 3,
   "dedup_ratio_raw_to_canonical": "1.0000",
   "raw_records_absorbed": 3
  },
  "rules": {
   "canonical": 3,
   "dedup_ratio_raw_to_canonical": "1.6666",
   "raw_records_absorbed": 5
  },
  "scenarios": {
   "canonical": 5,
   "dedup_ratio_raw_to_canonical": "1.0000",
   "raw_records_absorbed": 5
  },
  "tests": {
   "canonical": 1,
   "dedup_ratio_raw_to_canonical": "3.0000",
   "raw_records_absorbed": 3
  }
 },
 "by_partition_raw_set": {
  "SYN1": {
   "by_disposition": {
    "ALIAS_OF": 1,
    "CANONICAL": 9,
    "HISTORICAL_REVISION_OF": 1,
    "SOURCE_ONLY_ARTIFACT": 1,
    "TEST_INSTANCE_OR_EXECUTION_OCCURRENCE": 3,
    "UNRESOLVED": 1
   },
   "by_tier": {
    "EXECUTION_EVIDENCE": 1,
    "FIXTURE": 1,
    "GOVERNANCE_RULE": 4,
    "LOGICAL_SCENARIO": 5,
    "PARAMETRIZED_INSTANCE": 2,
    "RULE_ADJACENT": 1,
    "RULE_REVISION": 1,
    "TEST_IMPLEMENTATION": 1
   },
   "raw": 16,
   "unresolved": 1
  },
  "SYN2": {
   "by_disposition": {
    "ALIAS_OF": 1,
    "CANONICAL": 1,
    "HISTORICAL_REVISION_OF": 2,
    "TEST_INSTANCE_OR_EXECUTION_OCCURRENCE": 1
   },
   "by_tier": {
    "EXECUTION_EVIDENCE": 1,
    "FIXTURE": 2,
    "RULE_REVISION": 2
   },
   "raw": 5,
   "unresolved": 0
  }
 },
 "completeness_limitations": [
  "SYNTHETIC SAMPLE: invented content that exercises the tools; it is not the V0.1 corpus.",
  "The real partition outputs are loaded by a separate consolidation step and replace this sample.",
  "Informational catalogue only: non-authorizing, authority none, activates nothing, release and production remain on HOLD.",
  "Coverage rows are a derived projection of explicit links, not a qualification statement."
 ],
 "external_artifacts": [],
 "generation_tool": {
  "files": {
   "build_registry.py": "sha256:b618e34d1e6a0d0c3096e87631816b5224392be9e60fe5153483382a6891d46f",
   "load_partitions.py": "sha256:d2167c5cfe89c768ea0ce4b1a09e9799e7f1cbf339bb855f7a61d6877f99b63e",
   "validate_registry.py": "sha256:b717b1bef2285fef455aabc139c64a547914f3cc3de97655abf5ebd60624b4ec"
  },
  "name": "ocs-catalogue-tools",
  "revision": "sha256:618de86cef60fb2efbf8cb14f9c57171b50b5f72e6d2a248d4a607dd37fa7e9d"
 },
 "layer_counts": {
  "coverage": 8,
  "crosswalk": 21,
  "evidence": 2,
  "fixtures": 3,
  "lineage_sets": 1,
  "rules": 3,
  "scenarios": 5,
  "tests": 1
 },
 "layout": "full",
 "load_problems": [],
 "non_authorizing": true,
 "note_on_totals": "Per-set figures are not summed into a corpus total; global identity decisions are in the crosswalk.",
 "partition_count": 16,
 "raw_record_accounting": {
  "crosswalk_rows": 21,
  "each_raw_record_has_exactly_one_crosswalk_row": true,
  "note": "Checked by the validator per raw index and per committed inventory digest. Partition A has two raw files, reported as raw sets A and A2.",
  "per_raw_set": {
   "SYN1": 16,
   "SYN2": 5
  },
  "raw_records_in_inventory": 21
 },
 "regeneration": {},
 "relationship_provenance_by_layer": {
  "evidence": {
   "DERIVED": 0,
   "SOURCE_STATED": 2,
   "UNRESOLVED": 0
  },
  "rules": {
   "DERIVED": 3,
   "SOURCE_STATED": 4,
   "UNRESOLVED": 0
  },
  "scenarios": {
   "DERIVED": 0,
   "SOURCE_STATED": 6,
   "UNRESOLVED": 0
  },
  "tests": {
   "DERIVED": 0,
   "SOURCE_STATED": 3,
   "UNRESOLVED": 1
  }
 },
 "source_completeness_limitations": {
  "crosswalk_rows_without_a_recorded_source_repo": 0,
  "entries_without_a_recorded_source_revision_by_layer": {
   "fixtures": 0,
   "rules": 0,
   "scenarios": 0,
   "tests": 0
  },
  "evidence_records_whose_kind_the_source_did_not_state": 0,
  "evidence_without_a_recorded_source_revision_by_raw_set": {},
  "source_reference_links_recorded_on_entries": 0,
  "statement": "These counts are recorded as source-completeness limitations. The loader did not supply a revision, an evidence kind or a basis where the partition output stated none; such values read unrecorded or unknown."
 },
 "source_revisions_report": {
  "declared_revisions_checked_against_recorded": [
   {
    "component": "hub",
    "declared_short_revision": "a2d9396c",
    "declared_tag": "review-v0.1-g8-r10-20261022",
    "matching_recorded_revisions": [],
    "status": "not_found_in_recorded_revisions"
   },
   {
    "component": "institutional-governance",
    "declared_short_revision": "9b5ab721",
    "declared_tag": "review-v0.1-g8-r10-20261022",
    "matching_recorded_revisions": [],
    "status": "not_found_in_recorded_revisions"
   },
   {
    "component": "control-plane",
    "declared_short_revision": "0a41faa9",
    "declared_tag": "review-v0.1-g8-r10-20261022",
    "matching_recorded_revisions": [],
    "status": "not_found_in_recorded_revisions"
   },
   {
    "component": "action-manifest",
    "declared_short_revision": "fa170815",
    "declared_tag": "review-v0.1-g8-r10-20261022",
    "matching_recorded_revisions": [],
    "status": "not_found_in_recorded_revisions"
   },
   {
    "component": "execution-runtime",
    "declared_short_revision": "ec728da6",
    "declared_tag": "review-v0.1-g8-r10-20261022",
    "matching_recorded_revisions": [],
    "status": "not_found_in_recorded_revisions"
   },
   {
    "component": "replay-bundle",
    "declared_short_revision": "028f63d1",
    "declared_tag": "review-v0.1-g8-r10-20261022",
    "matching_recorded_revisions": [],
    "status": "not_found_in_recorded_revisions"
   },
   {
    "component": "governance-evidence-pack",
    "declared_short_revision": "a3ebbb90",
    "declared_tag": "review-v0.1-g8-r10-20261022",
    "matching_recorded_revisions": [],
    "status": "not_found_in_recorded_revisions"
   },
   {
    "component": "open-decision-evidence-standard",
    "declared_short_revision": "e86a25a1",
    "declared_tag": "review-v0.1-g8-r10-20261022",
    "matching_recorded_revisions": [],
    "status": "not_found_in_recorded_revisions"
   },
   {
    "component": "verifier",
    "declared_short_revision": "c0b8ba1f",
    "declared_tag": "review-v0.1-g8-r10-20261022",
    "matching_recorded_revisions": [],
    "status": "not_found_in_recorded_revisions"
   },
   {
    "component": "stack-qualification tag commit",
    "declared_short_revision": "195c728f",
    "declared_tag": "review-v0.1-g8-r10-20261022",
    "matching_recorded_revisions": [],
    "status": "not_found_in_recorded_revisions"
   },
   {
    "component": "governed-exchange",
    "declared_short_revision": "7f7569b0",
    "declared_tag": "review-v0.1-g8-r10-20261022",
    "matching_recorded_revisions": [],
    "status": "not_found_in_recorded_revisions"
   },
   {
    "component": "ergonomics",
    "declared_short_revision": "54807212",
    "declared_tag": "review-v0.1-g8-r10-20261022",
    "matching_recorded_revisions": [],
    "status": "not_found_in_recorded_revisions"
   }
  ],
  "post_tag_heads_reported_separately": [
   {
    "component": "stack-qualification main",
    "declared_short_revision": "4298247e",
    "declared_tag": null,
    "matching_recorded_revisions": [],
    "named_by": "named by the assembly brief as the main head beside the tag commit 195c728f",
    "status": "not_found_in_recorded_revisions"
   },
   {
    "component": "hub docs/mvp-recovery source of truth",
    "declared_short_revision": "5b76c58a",
    "declared_tag": null,
    "matching_recorded_revisions": [],
    "named_by": "named by the G2 denominator pass as its MVP source of truth",
    "status": "not_found_in_recorded_revisions"
   }
  ],
  "recorded_repo_revisions": [
   {
    "repo": "example/synthetic-source",
    "revision": "0000000000000000000000000000000000000000",
    "seen_in": [
     "SYN1",
     "SYN2",
     "entries"
    ]
   }
  ]
 },
 "unrecorded_source_revisions": {
  "crosswalk_rows_with_unrecorded_source_repo": 0,
  "entries_without_recorded_revision": 0,
  "evidence_without_recorded_revision": 0
 },
 "unresolved_accounting": {
  "crosswalk_unresolved_rows": 1,
  "entries_with_unrecorded_source_revision": 0,
  "entries_with_unresolved_mvp_applicability": 7,
  "evidence_unrecorded_source_revisions": 0,
  "unresolved_reference_placeholders": 1,
  "unresolved_relationships": 1
 },
 "unresolved_applicability_note": "7 of 12 entries (58.3%) keep an unresolved MVP applicability with the reason recorded. That share is not evidence that requirements are unimplemented and not a coverage claim: it only means no stated basis ties the entry to the fixed MVP profile.",
 "validator": "validate_registry.py: no findings"
}
```
