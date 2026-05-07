from policyengine_us.model_api import *


class medicaid_irs_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Gross income used for Medicaid MAGI filing-threshold checks"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/61",
        "https://www.law.cornell.edu/cfr/text/42/435.603#d_2",
    )

    def formula(person, period, parameters):
        total = 0
        for source in parameters(period).gov.irs.gross_income.sources:
            total += max_(0, add(person, period, [source]))
        return total
