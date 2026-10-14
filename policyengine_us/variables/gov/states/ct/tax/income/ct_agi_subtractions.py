from policyengine_us.model_api import *


class ct_agi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut subtractions from federal adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        # Sec. 12-701(a)(19), (a)(20)(B)(iii) and (xvi)
        "https://www.cga.ct.gov/current/pub/chap_229.htm#sec_12-701",
        # Lines 42 and 44
        "https://portal.ct.gov/-/media/drs/forms/2025/income/2025-ct-1040-instructions_1225.pdf#page=9",
    )
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ct.tax.income.subtractions
        # Dependents' income is not in federal AGI; they report it on their
        # own return, so person-level subtractions count only the head and
        # spouse.
        total_subtractions = tax_unit_non_dep_add(tax_unit, period, p.subtractions)
        # Prevent negative subtractions from acting as additions
        return max_(0, total_subtractions)
