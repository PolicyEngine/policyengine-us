from policyengine_us.model_api import *


class il_income_tax_rebate_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois income tax rebate eligible"
    defined_for = StateCode.IL
    unit = USD
    definition_period = YEAR
    reference = "https://www.ilga.gov/Documents/legislation/publicacts/102/PDF/102-0700.pdf#page=131"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.il.tax.income.credits.income_tax_rebate
        federal_agi = tax_unit("adjusted_gross_income", period)
        joint = tax_unit("tax_unit_is_joint", period)
        income_threshold = where(
            joint,
            p.amount.joint.thresholds[1],
            p.amount.other.thresholds[1],
        )
        return federal_agi < income_threshold
