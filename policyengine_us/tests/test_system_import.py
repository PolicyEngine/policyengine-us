"""Regression tests for the top-level package import.

These tests catch parameter-tree mismatches that block construction of
`CountryTaxBenefitSystem` at import time — including the
`breakdown` vs. parameter-children kind of mismatch that
`policyengine-core >= 3.24.0` raises as a hard error.

History: three separate PRs (#8045, #8049, #8051) each fixed a subset
of `range(a, b)` breakdown dimensions that declared fewer children than
the underlying parameter keys. Each partial fix still left other files
broken, so end users on intermediate releases (e.g. 1.645.0) continued
to hit `ValueError` at import time (issue #8055). This test loads the
whole system once, which will fail loudly on any future mismatch.
"""


def test_country_tax_benefit_system_constructs_cleanly():
    """Constructing the tax-benefit system runs parameter homogenization,
    which validates every `breakdown` declaration against its children.
    Any mismatch raises `ValueError` from
    `policyengine_core.parameters.operations.homogenize_parameters`.
    """
    from policyengine_us.system import CountryTaxBenefitSystem

    CountryTaxBenefitSystem()


def test_package_import_does_not_raise():
    """Smoke test: the top-level `policyengine_us` import triggers
    `system.py` module-load which in turn instantiates the tax-benefit
    system. A partial parameter-tree regression surfaces here before
    any simulation code runs (mirrors the failure Martin Holmer hit in
    issue #8055 under policyengine-us 1.644.0 / 1.645.0).
    """
    import importlib
    import policyengine_us

    importlib.reload(policyengine_us)
