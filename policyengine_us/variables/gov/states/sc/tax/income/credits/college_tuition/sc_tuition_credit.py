from policyengine_us.model_api import *


class sc_tuition_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina Tuition Credit"
    defined_for = StateCode.SC
    unit = USD
    definition_period = YEAR
    reference: "https://dor.sc.gov/forms-site/Forms/I319_2021.pdf#page=2"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.sc.tax.income.credits.college_tuition

        # line 1
        total_hours = tax_unit("total_college_hours", period)
        # line 2
        qualified_tuition_expenses = add(tax_unit, period, ["qualified_tuition_expenses"])
        # line 3
        annual_hour_requirement = p.annual_hour_requirement
        tuition_limit = p.max_amount.tuition * total_hours / annual_hour_requirement
        # line 7 (lesser of line 2 or 3 and multiply by rate)
        uncapped_credit = min_(qualified_tuition_expenses, tuition_limit) * p.rate
        
        # compare line 7 with credit max amount, take lesser amount 
        return min_(uncapped_credit, p.max_amount.credit)
