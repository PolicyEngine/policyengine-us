from policyengine_us.model_api import *


class ct_property_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Connecticut Property Tax Credit"
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        p = parameters(period).gov.states.ct.tax.income.credits.property_tax
        age_threshold = p.threshold.age
        age_eligible = (age_head | age_spouse) >= age_threshold
        return age_eligible

