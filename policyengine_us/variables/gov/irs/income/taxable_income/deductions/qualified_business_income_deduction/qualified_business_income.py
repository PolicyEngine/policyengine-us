from policyengine_us.model_api import *


class qualified_business_income(Variable):
    value_type = float
    entity = Person
    label = "Qualified business income"
    documentation = "Business income that qualifies for the qualified business income deduction."
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/199A#c"
    defined_for = "business_is_qualified"

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.deductions.qbi
        gross_qbi = 0
        for var in p.income_definition:
            gross_qbi += person(var, period) * person(
                var + "_would_be_qualified", period
            )
        qbi_deductions = add(person, period, p.deduction_definition)
        return max_(0, gross_qbi - qbi_deductions)
