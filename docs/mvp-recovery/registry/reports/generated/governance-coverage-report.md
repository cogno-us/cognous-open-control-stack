# Governance Coverage Report

Informational only. Non-authorizing; authority none; activates nothing; no rule, scenario or test was executed; release and production remain on HOLD.

Catalogue manifest: `sha256:75dd1f487b25248636e13cb8371e785db43e2962f9c9b139bb604314f649b24e` (registry 0.1.0, synthetic sample)

Source revisions:
- SYN1: example/synthetic-source@0000000000000000000000000000000000000000; 16 raw records; inventory `sha256:34fa0773397cccbfd7b2e3f21aebec177162808b2cab51775517671986147168`
- SYN2: example/synthetic-source@0000000000000000000000000000000000000000; 5 raw records; inventory `sha256:68c3606773266b7a98114c0c025f31e22e8355c870c79fa7b6a7a5222176f4fc`

```json
{
 "assessments_are_separate": "catalogue_completeness, implementation_coverage, test_coverage and independent_qualification are never inferred from one another; a historical verdict never transfers to a new candidate; a DERIVED link is a candidate only.",
 "authority": "none",
 "by_subject_layer": {
  "rules": {
   "catalogue_completeness": {
    "complete": 1,
    "has_unresolved": 2
   },
   "implementation_coverage": {
    "derived_candidate_only": 1,
    "none": 1,
    "source_stated_link": 1
   },
   "independent_qualification": {
    "none": 3
   },
   "test_coverage": {
    "none": 3
   }
  },
  "scenarios": {
   "catalogue_completeness": {
    "complete": 2,
    "has_unresolved": 3
   },
   "implementation_coverage": {
    "none": 4,
    "source_stated_link": 1
   },
   "independent_qualification": {
    "none": 5
   },
   "test_coverage": {
    "none": 4,
    "source_stated_link": 1
   }
  }
 },
 "non_authorizing": true,
 "rows": [
  {
   "assessments": {
    "catalogue_completeness": "has_unresolved",
    "implementation_coverage": "derived_candidate_only",
    "independent_qualification": "none",
    "test_coverage": "none"
   },
   "mvp_applicability": "unresolved",
   "states": [
    "defined"
   ],
   "subject_id": "R-SYN-floor-a-00000001"
  },
  {
   "assessments": {
    "catalogue_completeness": "has_unresolved",
    "implementation_coverage": "none",
    "independent_qualification": "none",
    "test_coverage": "none"
   },
   "mvp_applicability": "unresolved",
   "states": [
    "defined"
   ],
   "subject_id": "R-SYN-reason-c-00000003"
  },
  {
   "assessments": {
    "catalogue_completeness": "complete",
    "implementation_coverage": "source_stated_link",
    "independent_qualification": "none",
    "test_coverage": "none"
   },
   "mvp_applicability": "mvp_fixed",
   "states": [
    "defined",
    "implemented"
   ],
   "subject_id": "R-SYN-reg-b-00000002"
  },
  {
   "assessments": {
    "catalogue_completeness": "complete",
    "implementation_coverage": "source_stated_link",
    "independent_qualification": "none",
    "test_coverage": "source_stated_link"
   },
   "mvp_applicability": "mvp_fixed",
   "states": [
    "defined",
    "implemented",
    "tested"
   ],
   "subject_id": "S-SYN-case-1-00000001"
  },
  {
   "assessments": {
    "catalogue_completeness": "complete",
    "implementation_coverage": "none",
    "independent_qualification": "none",
    "test_coverage": "none"
   },
   "mvp_applicability": "requires_unavailable_component",
   "states": [
    "defined",
    "excluded_or_unsupported"
   ],
   "subject_id": "S-SYN-case-2-00000002"
  },
  {
   "assessments": {
    "catalogue_completeness": "has_unresolved",
    "implementation_coverage": "none",
    "independent_qualification": "none",
    "test_coverage": "none"
   },
   "mvp_applicability": "unresolved",
   "states": [
    "defined"
   ],
   "subject_id": "S-SYN-cofix-1-00000005"
  },
  {
   "assessments": {
    "catalogue_completeness": "has_unresolved",
    "implementation_coverage": "none",
    "independent_qualification": "none",
    "test_coverage": "none"
   },
   "mvp_applicability": "unresolved",
   "states": [
    "defined"
   ],
   "subject_id": "S-SYN-spec-1-00000004"
  },
  {
   "assessments": {
    "catalogue_completeness": "has_unresolved",
    "implementation_coverage": "none",
    "independent_qualification": "none",
    "test_coverage": "none"
   },
   "mvp_applicability": "unresolved",
   "states": [
    "defined"
   ],
   "subject_id": "S-SYN-suite-1-00000003"
  }
 ],
 "states_by_subject_layer": {
  "rules": {
   "defined": 3,
   "implemented": 1
  },
  "scenarios": {
   "defined": 5,
   "excluded_or_unsupported": 1,
   "implemented": 1,
   "tested": 1
  }
 }
}
```
