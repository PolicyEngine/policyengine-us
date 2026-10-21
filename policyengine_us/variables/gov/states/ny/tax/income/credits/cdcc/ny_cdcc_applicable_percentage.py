from policyengine_us.model_api import *


class ny_cdcc_applicable_percentage(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York child and dependent care credit applicable percentage"
    unit = "/1"
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (c-2)(2)(E)
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.credits.cdcc.decoupled.rate
        ny_agi = tax_unit("ny_agi", period)
        excess = max_(ny_agi - p.phase_down_threshold, 0)
        return max_(p.max - p.phase_down_rate * excess, p.min)
