from policyengine_us.model_api import *


class ct_property_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Connecticut Property Tax Credit"
    definition_period = YEAR
    defined_for = StateCode.CT
    # (b)(2)
    reference = "https://www.cga.ct.gov/current/pub/chap_229.htm#sec_12-704c"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ct.tax.income.credits.property_tax
        age_eligible = (
            tax_unit("greater_age_head_spouse", period) >= p.age_threshold
        )
        p = parameters(period).gov.states.ct.tax.income.credits.property_tax
        dependents_present = tax_unit("tax_unit_dependents", period) > 0

        return dependents_present | age_eligible
