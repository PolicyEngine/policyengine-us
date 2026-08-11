"""The BLS CPI files carry published monthly actuals through June 2026,
including the October 2025 gap (never published) and the replaced
projection points (#9091)."""

from policyengine_us.system import system


def _cpi(name):
    return getattr(system.parameters.gov.bls.cpi, name)


def test_cpi_w_monthly_actuals():
    cpi_w = _cpi("cpi_w")
    # June 2026 observed value (CWSR0000SA0).
    assert cpi_w("2026-06-01") == 325.641
    # October 2025 was never published: September carries forward.
    assert cpi_w("2025-10-01") == 317.477
    # The observed February replaces the derived 2026Q1 projection point.
    assert cpi_w("2026-02-01") == 320.266


def test_cpi_u_monthly_actuals():
    cpi_u = _cpi("cpi_u")
    assert cpi_u("2026-06-01") == 332.568
    assert cpi_u("2025-10-01") == 324.245
    assert cpi_u("2026-02-01") == 327.460


def test_c_cpi_u_monthly_actuals():
    c_cpi_u = _cpi("c_cpi_u")
    assert c_cpi_u("2026-06-01") == 184.992
    assert c_cpi_u("2025-10-01") == 180.196
    # The observed February replaces the annual projection point (183.1).
    assert c_cpi_u("2026-02-01") == 181.080
