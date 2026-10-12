"""The ACA benchmark premium index carries the published 2026 actual and
extends at the pre-2026 trend (#9092)."""

from policyengine_us.system import system


def test_2026_benchmark_premium_is_published_actual():
    uprating = system.parameters.gov.aca.benchmark_premium_uprating
    # KFF national average benchmark (SLCSP) premium for 2026.
    assert uprating("2026-01-01") == 625


def test_extension_keeps_pre_jump_trend():
    # The 2026 jump is a one-off level shift: long-run growth stays at the
    # 2024-2025 trend rather than compounding the jump.
    uprating = system.parameters.gov.aca.benchmark_premium_uprating
    trend = uprating("2025-01-01") / uprating("2024-01-01")
    for year in (2027, 2028):
        implied = uprating(f"{year}-01-01") / uprating(f"{year - 1}-01-01")
        assert abs(implied - trend) < 1e-9
