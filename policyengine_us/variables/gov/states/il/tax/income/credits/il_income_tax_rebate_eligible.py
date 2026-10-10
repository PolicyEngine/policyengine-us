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
        # Section 212.1(a): "A taxpayer who is claimed as a dependent on
        # another individual's return for that year is ineligible". Spouses
        # filing jointly are treated as a single taxpayer, so either spouse
        # being claimable bars the return.
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        return (federal_agi < income_threshold) & ~filer_is_dependent
