from policyengine_us.model_api import *


class mt_interest_exemption_person(Variable):
    value_type = float
    entity = Person
    label = "Montana interest exemption for each person"
    unit = USD
    definition_period = YEAR
    reference = "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/Form-2-2022-Instructions.pdf#page=25"
    defined_for = "mt_interest_exemption_eligible_person"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.exemptions.interest
        filing_status = person.tax_unit("filing_status", period)
        cap = p.cap[filing_status]
        interest_income = person("taxable_interest_income", period)
        return min_(cap, interest_income)
