"""
Connecticut TANF (annual aggregator for TFA benefits).
"""

from policyengine_us.model_api import *


class ct_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut TANF"
    definition_period = YEAR
    defined_for = StateCode.CT
    unit = USD
    documentation = (
        "Annual total of Connecticut Temporary Family Assistance (TFA) benefits. "
        "This variable aggregates monthly ct_tfa benefits over the year for use "
        "in the federal TANF calculation."
    )
    reference = (
        "Conn. Gen. Stat. § 17b-112 (TFA Program Authorization); "
        "Connecticut TANF State Plan 2024-2026; "
        "https://www.cga.ct.gov/current/pub/chap_319s.htm"
    )

    adds = ["ct_tfa"]
