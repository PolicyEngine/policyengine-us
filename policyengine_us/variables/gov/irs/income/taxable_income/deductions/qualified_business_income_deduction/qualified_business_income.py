from policyengine_us.model_api import *


class qualified_business_income(Variable):
    value_type = float
    entity = Person
    label = "Qualified business income"
    documentation = "Business income that qualifies for the qualified business income deduction."
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/199A#c"

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.deductions
        income_components = p.qbi.income_definition
        gross_qbi = add(person, period, income_components)
        deduction_components = p.qbi.deduction_definition
        qbi_deductions = add(person, period, deduction_components)
        adjusted_qbi = max_(0, gross_qbi - qbi_deductions)
        qualified = person("business_is_qualified", period)
        return adjusted_qbi * qualified
