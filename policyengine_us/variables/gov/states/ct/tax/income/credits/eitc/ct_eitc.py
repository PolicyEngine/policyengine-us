from policyengine_us.model_api import *


class ct_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut Earned Income Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://portal.ct.gov/-/media/drs/forms/2025/income/2025-ct-1040-instructions_1225.pdf#page=3",
        "https://www.cga.ct.gov/current/pub/chap_229.htm#sec_12-704e",
    )
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ct.tax.income.credits.eitc
        federal_eitc = tax_unit("eitc", period)
        base_credit = federal_eitc * p.match
        # Bonus amount for taxpayers eligible for CT EITC with at least one qualifying child (effective 2025)
        if p.qualifying_child_bonus.in_effect:
            eitc_eligible = federal_eitc > 0
            has_qualifying_child = tax_unit("eitc_child_count", period) > 0
            bonus = (
                eitc_eligible
                * has_qualifying_child
                * p.qualifying_child_bonus.amount
            )
            return base_credit + bonus
        return base_credit
