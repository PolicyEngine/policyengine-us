from policyengine_us.model_api import *


class mi_is_senior_for_tax(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Michigan filer is a senior"
    definition_period = YEAR
    reference = "http://legislature.mi.gov/doc.aspx?mcl-206-514"
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mi.tax.income
        return tax_unit("greater_age_head_spouse", period) >= p.senior_age
