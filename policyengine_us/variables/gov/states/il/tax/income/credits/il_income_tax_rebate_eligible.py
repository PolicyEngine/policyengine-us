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
        # Section 212.1(a): a taxpayer "who is claimed as a dependent on
        # another individual's return for that year, is ineligible". The
        # exclusion is per taxpayer, so a joint return qualifies while either
        # spouse is not claimed.
        has_eligible_filer = (
            tax_unit("head_spouse_count_not_dependent_elsewhere", period) > 0
        )
        return (federal_agi < income_threshold) & has_eligible_filer
