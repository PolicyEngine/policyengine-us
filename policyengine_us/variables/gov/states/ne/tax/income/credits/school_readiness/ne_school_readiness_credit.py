from policyengine_us.model_api import *


class ne_school_readiness_credit(Variable):
    value_type = float
    entity = Person
    label = "Nebraska school readiness tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://revenue.nebraska.gov/sites/default/files/doc/tax-forms/2024/f_Individual_Income_Tax_Booklet.pdf#page=2"

    defined_for = "ne_school_readiness_credit_eligible_worker"

    def formula(person, period, parameters):
        level = person(
            "ne_school_readiness_credit_child_care_worker_rating", period
        )
        p = parameters(
            period
        ).gov.states.ne.tax.income.credits.school_readiness.amount
        return p.refundable.calc(
            level
        )  # determine school readiness credit amount
