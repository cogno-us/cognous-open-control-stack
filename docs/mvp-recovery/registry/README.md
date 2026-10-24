# Layered governance catalogue (informational)

DRAFT. Non-authorizing: every record carries `authority: none` and `non_authorizing: true`. The catalogue activates nothing, selects no pin, executes no rule, scenario or test, and makes no qualification statement. Release and production remain on HOLD. Population of this catalogue is outside the MVP critical path; it does not change the fixed MVP profile.

The committed content is a small SYNTHETIC SAMPLE (`synthetic_sample: true` in the manifest). The real partition outputs are loaded later by a separate consolidation step through `tools/load_partitions.py`.

## Layers

| Layer | Directory | Schema | Identity | Meaning |
|---|---|---|---|---|
| L1 rules | `rules/` | `schemas/rules.schema.json` | `R-` id | Catalogue profile entry that references a rule by identity plus digest. For rules held in an `ocs-registry-record/0` record it carries `registry_id`, `record_digest`, `rule_id`, `version` and the `rule_digest` of the rule row. |
| L2 scenarios | `scenarios/` | `scenarios.schema.json` | `S-` id | Logical scenario with verbatim expected outcome, polarity, temporal/recovery flag and a `scenario_class` (`logical`, `suite_level_acceptance`, `adversarial_or_unexecuted_spec`). |
| L3 tests | `tests/` | `tests.schema.json` | `T-` id | Test implementation; parametrized instances are counted, never separate entries. |
| L4 fixtures | `fixtures/` | `fixtures.schema.json` | `F-` id | Reference plus content digest and locations; bytes are never copied. |
| L5 evidence index | `evidence-index/` | `evidence.schema.json` | evidence digest | Execution evidence, outside the rule catalogue. Verdicts are quoted verbatim and `current_qualification_effect` is always `none`. Source and artifact commitments are mandatory. |
| L6 coverage | `reports/` | `coverage.schema.json` | subject id | Derived projection (see below). |
| crosswalk | `crosswalk/` | `crosswalk.schema.json` | `(raw_set, raw_index)` | One row per raw record. |

Registry-record contracts are reused, not changed. `tools/registry_records.py`, the 2.1 note and the R0 contract are untouched; catalogue metadata sits in this separate non-authorizing profile. A registry record referenced by the catalogue is kept under `rules/registry-records/`, is checked with `validate_record`, and must contain advisory rules only. Hashing follows `tools/registry_records.py`: `sha256` over RFC 8785 canonical JSON (a record's `digest` excludes its own member). Partition hashes are `sha256` of the file bytes.

Every entry has `source`, `native_ids`, `aliases` (every merged alias is retained), `raw_refs`, `lineage` (historical revisions, never overwritten), `annotations` (verbatim carried fields; no authority keys), `relationships`, `release_scope` (`v0_1|post_v0_1|unknown`) and an explicit `mvp_applicability {value, reason}` with value one of `mvp_fixed | other_supported_historical_profile | requires_unavailable_component | needs_migration | historical_only | unresolved`. Rules also carry `normative_type` (`constitutional_floor | mandatory | conditional | advisory | principle | reason_code_or_refusal_vocabulary | validator_rule | requirement_row | decision | unknown`) and `adoption_status`; only adopted CR-001..CR-035 identities may be a `constitutional_floor`.

## Relationship provenance (R1)

Each reference (rule to scenario, scenario to test, test to evidence, and so on) has one relationship record: `SOURCE_STATED` (exact repo, revision, location), `DERIVED` (method, supporting refs, confidence class `high|medium|low|heuristic`, no source claim) or `UNRESOLVED` (names the missing evidence). The flags `establishes_enforcement`, `establishes_test_coverage` and `establishes_qualification` are always `false`. An `UNRESOLVED:` target cannot carry another provenance.

## Coverage (R2) and denominators (R3)

Coverage rows hold four separate assessments, none inferred from another: `catalogue_completeness`, `implementation_coverage`, `test_coverage`, `independent_qualification`. A `DERIVED` link is only a candidate (`derived_candidate_only`). `implemented` needs a source-stated test link; `tested` needs a source-stated run-result evidence link; `independently_qualified` needs a source-stated independent qualification record, which a run result or historical verdict never is. `excluded_or_unsupported` follows `requires_unavailable_component` or `historical_only`. The validator recomputes every row and refuses any difference.

`tools/generate_reports.py` writes `reports/generated/` (not hashed by the manifest because it names the manifest): the Catalogue Integrity Report, the Governance Coverage Report and the Denominator Report, each naming the exact manifest digest and source revisions. The Denominator Report keeps ten denominators apart and has no headline scenario count: rules by normative type, logical scenarios, suite-level acceptance scenarios, adversarial or unexecuted specifications, test implementations, parametrized instances, fixtures, historical execution records, distinct execution identities, historical verdicts.

## Manifest

`manifest.json` (`ocs-catalogue-manifest/0`): registry version, schema versions, source inventory commitments (raw record count and an inventory digest per raw set, with source repo revisions), per-partition `sha256`, record count and key range, per-layer counts, `unresolved_accounting`, registry-record pins, generation-tool revision (hashes of the generator and validator) and completeness limitations. Partitions are split by layer, source family (from the id) and ID range, in files of at most 200 records.

## Commands (stdlib only, offline)

```
python3 -I docs/mvp-recovery/registry/tools/validate_registry.py [--root DIR] [--previous DIR]
python3 -I docs/mvp-recovery/registry/tools/generate_reports.py [--root DIR] [--check]
python3 -I docs/mvp-recovery/registry/tools/build_registry.py --sample
python3 -I docs/mvp-recovery/registry/tools/load_partitions.py --in OUT --partitions A B C D R4 [--overlay OUT/global/G1 ...] --out DIR
PYTHONPATH=. python3 -m pytest -q tests/test_registry_catalogue.py
```

The validator refuses (codes in brackets): a raw record missing or repeated in the crosswalk, or a changed raw digest [crosswalk_*, inventory_commitment_mismatch]; duplicate ids per namespace [duplicate_id, namespace_mismatch]; unresolved typed references [unresolved_reference]; rule/scenario links that disagree [link_not_bidirectional]; evidence without source or artifact commitments [evidence_commitment_missing]; dropped aliases or lineage [alias_not_retained, revision_not_retained]; overwritten or removed history against `--previous` [historical_*]; unclassified MVP applicability [record_schema]; evidence presented as a rule [evidence_as_rule]; coverage not derivable from explicit links [coverage_inferred]; any `authority` other than `none` [authority_promotion]; partition hash, count, range or manifest digest mismatch; missing, orphaned or mis-provenanced relationships and promoted unresolved links [relationship_*, unresolved_promoted]; unresolved counts that differ from the manifest [unresolved_accounting_mismatch].

## Loader contract

Input per partition `P` under `OUT/P/`: `P.canonical.json` (keys `rules`, `logical_scenarios`, `test_implementations`, `fixtures`; each an inline list or pointers `{file,count,sha256}` to shards `{entries:[...]}`), `P.crosswalk.json` (inline `rows` or `parts` pointers; catalogue dispositions with `target`, or the legacy `CANONICAL:<id>`, `ATTACHED_TO:<id>`, `EVIDENCE_INDEXED:<digest>`, `SOURCE_REFERENCE_ONLY`, `UNRESOLVED:<reason>` forms), `P.evidence-index.json`. Optional overlays (`OUT/global/G1|G2|G3`): `{"overlay":"identity","merges":[{into,from,basis}]}`, `{"overlay":"attributes","items":{id:{normative_type,adoption_status,scenario_class,release_scope,mvp_applicability}}}`, `{"overlay":"relationships","items":[{owner,field,to,provenance,...}]}`. The loader guesses nothing: missing attributes become unknown or unresolved, links without provenance become `UNRESOLVED`, merges need a stated basis, and a canonical id emitted by two partitions with different identity refuses the load. Partition totals are never summed before identity resolution.

## Limitations

The validator checks internal consistency, not the truth of source claims, the correctness of a tool run or the presence of source bytes. Raw record content is not read by the validator; only its digest commitments are. A passing validation is not a qualification, acceptance or release statement.
