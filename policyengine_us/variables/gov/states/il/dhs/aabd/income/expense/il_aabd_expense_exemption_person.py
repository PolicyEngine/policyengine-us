from policyengine_us.model_api import *


class il_aabd_expense_exemption_person(Variable):
    value_type = float
    entity = Person
    label = "Illinois Aid to the Aged, Blind or Disabled (AABD) expense exemption per person"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.IL
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.125",
    )

    adds = "gov.states.il.dhs.aabd.income.exemption.sources"
