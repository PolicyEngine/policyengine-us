from policyengine_us.model_api import *


class il_aabd_flat_exemption_excess_over_unearned_income(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Illinois Aid to the Aged, Blind or Disabled (AABD) flat exemption excess over unearned income"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.dhs.aabd.income.exemption
        countable_unearned_income = person(
            "il_aabd_countable_unearned_income", period
        )
        return max_(p.flat - countable_unearned_income, 0)
