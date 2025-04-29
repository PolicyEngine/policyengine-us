from policyengine_us.model_api import *


class il_aabd_gross_unearned_income(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Illinois Aid to the Aged, Blind or Disabled (AABD) gross unearned income"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.100"
    defined_for = StateCode.IL

    adds = "gov.states.il.dhs.aabd.income.sources.unearned"
