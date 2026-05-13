from policyengine_us.model_api import *


class ct_chip_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut HUSKY B annual premium"
    unit = USD
    documentation = (
        "Annual Connecticut HUSKY B (separate CHIP) premium paid by the tax "
        "unit. Band 1 families (below 254% FPL) pay no premium; Band 2 "
        "families pay a per-child monthly premium capped at the family "
        "maximum, annualized."
    )
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = "https://portal.ct.gov/-/media/hh/pdf/husky-health-monthly-income-chart-march-1-2025.pdf"

    def formula(tax_unit, period, parameters):
        n_chip_children = add(tax_unit, period, ["is_chip_eligible_child"])
        income_level = tax_unit("tax_unit_medicaid_income_level", period)
        p = parameters(period).gov.states.ct.hhs.chip.premium
        per_child = p.per_child.calc(income_level)
        family_cap = p.family_cap.calc(income_level)
        monthly = min_(n_chip_children * per_child, family_cap)
        return monthly * MONTHS_IN_YEAR
