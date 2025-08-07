from policyengine_us.model_api import *


class il_aabd_countable_unearned_income(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Illinois Aid to the Aged, Blind or Disabled (AABD) countable unearned income"
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.120",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.dhs.aabd.income.exemption
        gross_unearned_income = person("il_aabd_gross_unearned_income", period)
        return max_(gross_unearned_income - p.flat, 0)
