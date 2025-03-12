from policyengine_us.model_api import *


class sc_sales_and_use_exclusion_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for South Carolina sales and use tax senior exclusion"
    definition_period = YEAR
    reference = "https://dor.sc.gov/resources-site/lawandpolicy/Advisory%20Opinions/RR08-5.pdf#page=2"
    defined_for = StateCode.SC

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.sc.tax.sales_and_use.exclusion
        person = tax_unit.members
        age = person("age", period)
        age_eligible = age >= p.age_threshold
        return age_eligible
