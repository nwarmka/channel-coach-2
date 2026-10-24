"""Read-only voiceover studio launch readiness assessment.

A missing requirement must never be interpreted as authorization to generate
commercial audio, charge credits, or expose private media.
"""

REQUIRED_LAUNCH_CHECKS = (
    "elevenlabs_commercial_rights_verified",
    "provider_cost_margin_reviewed",
    "atomic_credit_reservation_deployed",
    "idempotent_refund_path_deployed",
    "private_storage_rls_verified",
    "script_project_rls_verified",
    "signed_download_authorization_verified",
    "studio_authenticated_ui_integrated",
    "end_to_end_tests_passed",
)


def assess_voiceover_launch_readiness(verified_checks=None):
    checks = verified_checks or {}
    if not isinstance(checks, dict):
        raise ValueError("Readiness checks must be a mapping.")
    missing = [name for name in REQUIRED_LAUNCH_CHECKS
               if checks.get(name) is not True]
    return {
        "ready": not missing,
        "missing": missing,
        "generation_enabled": False,
        "billing_enabled": False,
        "note": (
            "Readiness is advisory. Deployment and commercial generation "
            "require separate explicit approval."
        ),
    }
