from policyengine_us.model_api import *


class mt_married_filing_separately_on_same_return_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Montana married filing separately on same return"
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-42.15.322",
        "https://leg.mt.gov/bills/2021/SB0399/SB0399_3.pdf#page=31",
    )

    def formula(person, period, parameters):
        return parameters(
            period
        ).gov.states.mt.tax.income.married_filing_separately_on_same_return_allowed
