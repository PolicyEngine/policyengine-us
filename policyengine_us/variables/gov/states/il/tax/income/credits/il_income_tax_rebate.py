from policyengine_us.model_api import *


class il_income_tax_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois income tax rebate"
    defined_for = "il_income_tax_rebate_eligible"
    unit = USD
    definition_period = YEAR
    reference = "https://codes.findlaw.com/il/chapter-35-revenue/il-st-sect-35-5-212-1.html"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.il.tax.income.credits.income_tax_rebate
        federal_agi = tax_unit("adjusted_gross_income", period)
        joint = tax_unit("tax_unit_is_joint", period)
        base_amount = where(
            joint,
            p.amount.joint.calc(federal_agi),
            p.amount.other.calc(federal_agi),
        )
        dependent_count = tax_unit("tax_unit_dependents", period)
        capped_dependents = min_(dependent_count, p.max_dependents)
        dependent_amount = capped_dependents * p.amount.dependent
        return base_amount + dependent_amount
