"""Synthetic observation assurance; no authority issuance or execution permission."""
from dataclasses import asdict, dataclass
import hashlib
import hmac
import json
import math
from typing import Callable

CONTRACT = "synthetic-authority-observation/1"
STATUSES = {"CURRENT_VALID", "HISTORICAL_VALID", "REVOKED", "SUSPENDED", "SUPERSEDED", "UNKNOWN"}


def canonical(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def finite(value) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


@dataclass(frozen=True)
class ObjectBinding:
    institution: str
    domain: str
    object_class: str
    object_id: str
    scope_digest: str

    def __post_init__(self):
        if any(not isinstance(x, str) or not x.strip() for x in asdict(self).values()):
            raise ValueError("exact nonempty object bindings required")


@dataclass(frozen=True)
class SourceProfile:
    source_id: str
    version: str
    binding: ObjectBinding
    key: bytes
    max_age: float
    clock_skew: float
    minimum_revision: int

    def __post_init__(self):
        if not isinstance(self.binding, ObjectBinding):
            raise ValueError("typed binding required")
        if any(not isinstance(x, str) or not x.strip() for x in (self.source_id, self.version)):
            raise ValueError("source identity and version required")
        if type(self.key) is not bytes or len(self.key) < 32:
            raise ValueError("synthetic HMAC fixture key must contain at least 32 bytes")
        if not finite(self.max_age) or self.max_age < 0 or not finite(self.clock_skew) or self.clock_skew < 0:
            raise ValueError("finite nonnegative time bounds required")
        if type(self.minimum_revision) is not int or self.minimum_revision < 0:
            raise ValueError("trusted nonnegative revision floor required")


def sign_fixture(profile: SourceProfile, observation: dict) -> dict:
    """Test source only. Sharing this key is not enterprise source authentication."""
    payload = json.loads(canonical(observation))
    return {"observation": payload, "mac": hmac.new(profile.key, canonical(payload), hashlib.sha256).hexdigest()}


def _check(profile, response, now):
    if not isinstance(response, dict) or set(response) != {"observation", "mac"}:
        return "UNAUTHENTICATED", None
    record, mac = response["observation"], response["mac"]
    if not isinstance(record, dict) or not isinstance(mac, str):
        return "UNAUTHENTICATED", None
    try:
        raw = canonical(record)
        expected = hmac.new(profile.key, raw, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(mac, expected):
            return "UNAUTHENTICATED", None
        record = json.loads(raw)  # retained detached snapshot of exactly authenticated fields
    except (ValueError, TypeError, OverflowError):
        return "UNAUTHENTICATED", None
    fields = {"contract", "source_id", "profile_version", "binding", "revision", "status", "observed_at", "effective_at", "valid_until", "facts_digest"}
    if set(record) != fields:
        return "UNKNOWN", record
    if (record["contract"] != CONTRACT or record["source_id"] != profile.source_id
            or record["profile_version"] != profile.version or record["binding"] != asdict(profile.binding)):
        return "OUT_OF_SCOPE", record
    if type(record["revision"]) is not int or record["revision"] < 0:
        return "UNKNOWN", record
    if record["revision"] < profile.minimum_revision:
        return "STALE", record
    if not isinstance(record["status"], str) or record["status"] not in STATUSES:
        return "UNKNOWN", record
    if not isinstance(record["facts_digest"], str) or len(record["facts_digest"]) != 64 or any(c not in "0123456789abcdef" for c in record["facts_digest"]):
        return "UNKNOWN", record
    observed, effective, until = (record[x] for x in ("observed_at", "effective_at", "valid_until"))
    if not all(finite(x) for x in (observed, effective, until)) or until <= effective or effective > observed:
        return "UNKNOWN", record
    if observed > now + profile.clock_skew or effective > now or now - observed > profile.max_age or now >= until:
        return "STALE", record
    return record["status"], record


def resolve_observations(profiles: tuple[SourceProfile, ...], lookup: Callable[[SourceProfile], dict], *, now: float) -> dict:
    """Resolve one exact object through trusted configured source adapters.

    Caller supplies evaluation clock, profiles, revision floors and adapters as trusted
    host configuration. Never populate these from an incoming agent request.
    """
    profiles = tuple(profiles)
    if not finite(now) or not profiles or any(not isinstance(p, SourceProfile) for p in profiles):
        raise ValueError("trusted finite clock and nonempty source profiles required")
    if len({p.source_id for p in profiles}) != len(profiles):
        raise ValueError("duplicate source identities")
    if any(p.binding != profiles[0].binding for p in profiles):
        raise ValueError("all authoritative sources must resolve the same exact object")
    observations = []
    for profile in profiles:
        try:
            response = lookup(profile)
        except Exception:
            classification, record = "UNKNOWN", None
        else:
            classification, record = _check(profile, response, now)
        observations.append({"source_id": profile.source_id, "profile_version": profile.version,
                             "max_age": profile.max_age, "clock_skew": profile.clock_skew,
                             "minimum_revision": profile.minimum_revision,
                             "classification": classification, "observation": record})
    classes = {entry["classification"] for entry in observations}
    # Preserve all disagreements; there is no permissive winner or majority vote.
    valid_facts = {entry["observation"]["facts_digest"] for entry in observations
                   if entry["classification"] == "CURRENT_VALID"}
    if len(classes) > 1 or len(valid_facts) > 1:
        classification = "CONFLICT"
    else:
        classification = next(iter(classes))
    report = {"contract": CONTRACT, "evaluated_at": now, "binding": asdict(profiles[0].binding),
              "classification": classification, "observations": observations,
              "hold": classification != "CURRENT_VALID", "authorizes_execution": False,
              "production_qualified": False}
    report["evidence_digest"] = hashlib.sha256(canonical(report)).hexdigest()
    return report
