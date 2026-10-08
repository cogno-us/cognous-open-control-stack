"""Bounded synthetic source tests; not the complete A1--A18 campaign."""
from dataclasses import asdict, replace
import unittest
from reference_profiles.resolver_assurance import CONTRACT, ObjectBinding, SourceProfile, resolve_observations, sign_fixture


class ResolverAssuranceTests(unittest.TestCase):
    def setUp(self):
        self.profile = SourceProfile("grant-source", "1", ObjectBinding("institution", "domain", "grant", "g1", "scope1"), b"fixture-key-not-for-production-00", 10, 1, 3)
        self.record = {"contract": CONTRACT, "source_id": "grant-source", "profile_version": "1", "binding": asdict(self.profile.binding), "revision": 3, "status": "CURRENT_VALID", "observed_at": 95, "effective_at": 90, "valid_until": 110, "facts_digest": "a" * 64}

    def resolve(self, **updates):
        record = dict(self.record, **updates)
        return resolve_observations((self.profile,), lambda _: sign_fixture(self.profile, record), now=100)

    def test_current_is_not_permission(self):
        result = self.resolve()
        self.assertEqual(result["classification"], "CURRENT_VALID")
        self.assertFalse(result["authorizes_execution"])
        self.assertFalse(result["production_qualified"])

    def test_historical_cannot_be_current(self):
        self.assertEqual(self.resolve(status="HISTORICAL_VALID")["classification"], "HISTORICAL_VALID")
        self.assertTrue(self.resolve(status="HISTORICAL_VALID")["hold"])

    def test_prospective_statuses_hold(self):
        for status in ("REVOKED", "SUSPENDED", "SUPERSEDED", "UNKNOWN"):
            with self.subTest(status=status):
                self.assertTrue(self.resolve(status=status)["hold"])

    def test_exact_binding(self):
        for field in asdict(self.profile.binding):
            with self.subTest(field=field):
                binding = dict(asdict(self.profile.binding), **{field: "wrong"})
                self.assertEqual(self.resolve(binding=binding)["classification"], "OUT_OF_SCOPE")

    def test_source_and_contract_pins(self):
        for field in ("contract", "source_id", "profile_version"):
            with self.subTest(field=field):
                self.assertEqual(self.resolve(**{field: "wrong"})["classification"], "OUT_OF_SCOPE")

    def test_rollback_floor(self):
        self.assertEqual(self.resolve(revision=2)["classification"], "STALE")

    def test_freshness_boundary(self):
        self.assertEqual(self.resolve(observed_at=90)["classification"], "CURRENT_VALID")
        self.assertEqual(self.resolve(observed_at=89, effective_at=88)["classification"], "STALE")

    def test_expiry_boundary(self):
        self.assertEqual(self.resolve(valid_until=100)["classification"], "STALE")

    def test_future_observation(self):
        self.assertEqual(self.resolve(observed_at=102)["classification"], "STALE")

    def test_future_effective_time(self):
        self.assertEqual(self.resolve(observed_at=101, effective_at=101)["classification"], "STALE")

    def test_malformed_time_and_revision(self):
        for field, value in (("observed_at", True), ("valid_until", "110"), ("revision", True), ("revision", -1), ("effective_at", 96), ("valid_until", 89)):
            with self.subTest(field=field, value=value):
                self.assertTrue(self.resolve(**{field: value})["hold"])

    def test_bad_mac_or_wrong_key(self):
        response = sign_fixture(self.profile, self.record)
        response["observation"]["revision"] = 99
        result = resolve_observations((self.profile,), lambda _: response, now=100)
        self.assertEqual(result["classification"], "UNAUTHENTICATED")
        self.assertIsNone(result["observations"][0]["observation"])
        forged = sign_fixture(replace(self.profile, key=b"x"*32), self.record)
        self.assertEqual(resolve_observations((self.profile,), lambda _: forged, now=100)["classification"], "UNAUTHENTICATED")

    def test_self_assertion_is_not_authenticated(self):
        result = resolve_observations((self.profile,), lambda _: dict(self.record, authenticated=True), now=100)
        self.assertEqual(result["classification"], "UNAUTHENTICATED")

    def test_outage_holds_without_cache(self):
        def unavailable(_):
            raise OSError("fixture offline")
        self.assertEqual(resolve_observations((self.profile,), unavailable, now=100)["classification"], "UNKNOWN")

    def test_conflicting_sources_preserved(self):
        second = replace(self.profile, source_id="second", key=b"s"*32)
        def lookup(profile):
            return sign_fixture(profile, dict(self.record, source_id=profile.source_id, status="REVOKED" if profile == second else "CURRENT_VALID"))
        result = resolve_observations((self.profile, second), lookup, now=100)
        self.assertEqual(result["classification"], "CONFLICT")
        self.assertEqual(len(result["observations"]), 2)

    def test_conflicting_facts_hold_even_same_status(self):
        second = replace(self.profile, source_id="second")
        def lookup(profile):
            return sign_fixture(profile, dict(self.record, source_id=profile.source_id, facts_digest=("b" if profile == second else "a")*64))
        self.assertEqual(resolve_observations((self.profile, second), lookup, now=100)["classification"], "CONFLICT")

    def test_prior_report_preserved_on_later_revocation(self):
        previous = self.resolve()
        revoked = self.resolve(status="REVOKED")
        self.assertEqual(previous["classification"], "CURRENT_VALID")
        self.assertNotEqual(previous["evidence_digest"], revoked["evidence_digest"])

    def test_detached_authenticated_snapshot(self):
        response = sign_fixture(self.profile, self.record)
        result = resolve_observations((self.profile,), lambda _: response, now=100)
        response["observation"]["status"] = "REVOKED"
        self.assertEqual(result["observations"][0]["observation"]["status"], "CURRENT_VALID")

    def test_invalid_configuration(self):
        for updates in ({"minimum_revision": True}, {"max_age": float("nan")}, {"clock_skew": -1}, {"key": b"short"}):
            with self.subTest(updates=updates), self.assertRaises(ValueError):
                replace(self.profile, **updates)
        for profiles in ((), (self.profile, self.profile), (self.profile, replace(self.profile, source_id="other", binding=replace(self.profile.binding, institution="other")))):
            with self.subTest(profiles=profiles), self.assertRaises(ValueError):
                resolve_observations(profiles, lambda _: {}, now=100)
        for now in (float("inf"), float("nan"), True):
            with self.subTest(now=now), self.assertRaises(ValueError):
                resolve_observations((self.profile,), lambda _: {}, now=now)

    def test_unknown_fields_status_and_bad_digest_hold(self):
        for updates in ({"unexpected": True}, {"status": "ALLOW"}, {"status": []}, {"facts_digest": "invalid"}):
            with self.subTest(updates=updates):
                self.assertTrue(self.resolve(**updates)["hold"])


if __name__ == "__main__":
    unittest.main()
