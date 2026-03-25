"""Required fields and sections per spec type."""

# Fields required in YAML frontmatter for all specs
REQUIRED_FIELDS_ALL = ["spec_name", "spec_version", "category", "tier"]

# Additional fields required for Core tier specs
REQUIRED_FIELDS_CORE = ["priority", "domain"]

# Valid tier values
VALID_TIERS = {"core", "extended"}

# Valid priority values
VALID_PRIORITIES = {"very high", "high", "medium", "low"}

# Required markdown sections (## headings) per spec type.
# Only specs with known section requirements are listed here.
# All others get frontmatter-only validation.
REQUIRED_SECTIONS: dict[str, list[str]] = {
    "SOUL.md": ["Purpose", "Personality", "Values"],
    "ESCALATION.md": ["Levels", "Triggers", "Contacts"],
    "LIMITS.md": ["Hard Limits", "Soft Limits"],
    "TEAM.md": ["Members", "Coordination"],
    "WHOAMI.md": ["Identity", "Verification"],
    "INPUT.md": ["Accepted Formats", "Validation"],
    "OUTPUT.md": ["Output Formats", "Schema"],
    "DELEGATION.md": ["Delegating Principal", "Delegation Scope", "Revocation"],
    "ATTESTATION.md": ["Attestation Method", "Credential Lifecycle"],
    "AUDITTRAIL.md": ["Audit Event Schema", "Tamper Resistance"],
    "SESSION.md": ["Session Identity", "Session Boundaries", "Destruction Policy"],
    "ENFORCEMENT.md": ["Pre-Deployment Validation", "Runtime Enforcement Matrix"],
    "INTENT.md": ["Intent Declaration Format", "Confidence Level"],
    "LEASTPRIVILEGE.md": ["Privilege Baseline", "Just-In-Time Escalation"],
    "PROMPTSHIELD.md": ["Direct Injection Controls", "Detection Methods"],
    "PROVENANCE.md": ["Input Source Registry", "Contamination Policy"],
    "CONSENT.md": ["Consent Requirements", "Consent Collection", "Consent Record", "Consent Revocation"],
    "SHAREDCONTEXT.md": ["Access Control Matrix", "Memory Schema", "Retention Policy"],
    "MEMORYSAFETY.md": ["Threat Model", "Input Sanitization", "Poisoning Detection", "Quarantine Procedures"],
    "CIRCUITBREAKER.md": ["Circuit Breaker States", "Failure Thresholds", "Blast Radius Boundaries", "Fallback Behaviors"],
}

# Specs that are known to cross-reference other specs.
# Maps spec name -> list of spec names it commonly references.
COMMON_CROSS_REFS: dict[str, list[str]] = {
    "TEAM.md": ["WHOAMI.md"],
    "DELEGATION.md": ["WHOAMI.md", "PERMISSIONS.md", "AUDITTRAIL.md"],
    "ESCALATION.md": ["LIMITS.md"],
    "ENFORCEMENT.md": ["AUDITTRAIL.md", "ATTESTATION.md"],
    "SESSION.md": ["ID.md", "WAKEUP.md", "DELEGATION.md"],
}
