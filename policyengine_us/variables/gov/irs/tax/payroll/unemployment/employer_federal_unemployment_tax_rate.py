from policyengine_us.model_api import *


class employer_federal_unemployment_tax_rate(Variable):
    value_type = float
    entity = Person
    label = "Employer federal unemployment tax rate"
    documentation = (
        "Effective federal unemployment tax rate, including any state credit "
        "reduction. Assumes wages are subject to state unemployment tax and "
        "state taxes are paid on time."
    )
    definition_period = YEAR
    unit = "/1"

    def formula(person, period, parameters):
        federal_unemployment = parameters(period).gov.irs.payroll.federal_unemployment
        state_code = person.household("state_code", period)
        return (
            federal_unemployment.effective_rate
            + federal_unemployment.credit_reduction_rate[state_code]
        )
