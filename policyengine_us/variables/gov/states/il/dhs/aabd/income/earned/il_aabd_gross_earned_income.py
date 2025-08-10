from policyengine_us.model_api import *


class il_aabd_gross_earned_income(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Illinois Aid to the Aged, Blind or Disabled (AABD) gross earned income"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.112"
    defined_for = StateCode.IL

    adds = "gov.states.il.dhs.aabd.income.sources.earned"
