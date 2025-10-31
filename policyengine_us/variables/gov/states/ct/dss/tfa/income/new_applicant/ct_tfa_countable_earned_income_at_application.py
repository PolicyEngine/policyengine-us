from policyengine_us.model_api import *


class ct_tfa_countable_earned_income_at_application(Variable):
    value_type = float
    entity = Person
    label = "Connecticut Temporary Family Assistance (TFA) countable earned income at application per person"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CT

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ct.dss.tfa.income.deduction.new_applicant
        gross_earned_income = person("tanf_gross_earned_income", period)

        return max_(gross_earned_income - p.amount, 0)
