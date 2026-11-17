from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.il.dhs.aabd.income.expense._child_care_exemption import (
    il_aabd_child_care_exemption,
)


class il_aabd_child_care_expense_exemption(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = (
        "Illinois Aid to the Aged, Blind or Disabled (AABD) childcare expense exemption"
    )
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.125",  # b
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        return il_aabd_child_care_exemption(
            person,
            period,
            parameters,
            person.spm_unit("childcare_expenses", period),
        )
