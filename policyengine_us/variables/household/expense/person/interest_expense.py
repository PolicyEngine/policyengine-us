from policyengine_us.model_api import *


class interest_expense(Variable):
    value_type = float
    entity = Person
    label = "Interest paid on all loans"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.interest.mortgage
        mortgage_interest = person("mortgage_interest", period)
        filing_status = person.tax_unit("filing_status", period)
        cap = p.cap[filing_status]
        capped_mortgage_interest = min_(mortgage_interest, cap)
        non_mortgage_interest = person("non_mortgage_interest", period)
        return capped_mortgage_interest + non_mortgage_interest
