from policyengine_us.model_api import *


class taxable_long_term_care_per_diem_benefits(Variable):
    value_type = float
    entity = Person
    label = "Taxable per diem long-term care benefits"
    documentation = "Form 8853 Section C: per diem payments above the greater of the daily limit times days and actual costs, less reimbursements (Schedule 1 line 8e)."
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/7702B#d",
        "https://www.irs.gov/instructions/i8853",
    )

    def formula(person, period, parameters):
        limit = parameters(period).gov.irs.gross_income.long_term_care_per_diem_limit
        benefits = max_(0, person("long_term_care_per_diem_benefits", period))
        daily_limit = limit * person("long_term_care_per_diem_days", period)
        costs = max_(0, person("long_term_care_qualified_costs", period))
        excludable = max_(
            0,
            max_(daily_limit, costs)
            - max_(0, person("long_term_care_cost_reimbursements", period)),
        )
        return max_(0, benefits - excludable)
