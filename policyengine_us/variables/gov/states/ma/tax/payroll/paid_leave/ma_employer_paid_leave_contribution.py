from policyengine_us.model_api import *


class ma_employer_paid_leave_contribution(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts employer paid leave contribution"
    documentation = (
        "Employer-side Massachusetts Paid Family and Medical Leave contribution, "
        "using employer headcount as a proxy for covered individuals."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        rate = person("ma_employer_paid_leave_contribution_rate", period)
        return rate * person("ma_paid_leave_taxable_wages", period)
