from policyengine_us.model_api import *


class ct_property_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Connecticut Property Tax Credit"
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ct.tax.income.credits.property_tax
        if p.eligibility_available:
            age_head = tax_unit("age_head", period)
            age_spouse = tax_unit("age_spouse", period)
            p = parameters(
                period
            ).gov.states.ct.tax.income.credits.property_tax
            dependents_present = tax_unit("tax_unit_dependents", period) > 0
            age_eligible = (age_head | age_spouse) >= p.threshold.age

            return dependents_present | age_eligible
        else:
            return True
