from policyengine_us.model_api import *


class sc_college_tuition_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina College Tuition Credit"
    defined_for = StateCode.SC
    unit = USD
    definition_period = YEAR
    reference: "https://dor.sc.gov/forms-site/Forms/I319_2022.pdf"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.sc.tax.income.credits.college_tuition

        # line 1
        total_hours = tax_unit("sc_total_hours", period)
        # line 2
        qualified_tuition = tax_unit("sc_qualified_tuition", period)
        # line 3
        annual_hour_requirement = p.annual_hour_requirement
        tuition_limit = p.tuition_limit * total_hours / annual_hour_requirement

        return min_(
            min_(qualified_tuition, tuition_limit) * p.rate, p.credit_limit
        )
