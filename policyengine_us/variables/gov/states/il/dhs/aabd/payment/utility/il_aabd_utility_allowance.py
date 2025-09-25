from policyengine_us.model_api import *


class il_aabd_utility_allowance(Variable):
    value_type = float
    entity = SPMUnit
    label = (
        "Illinois Aid to the Aged, Blind or Disabled (AABD) utility allowance"
    )
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.IL
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.259",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dhs.aabd.payment
        size = spm_unit("spm_unit_size", period)
        capped_size = clip(size, 1, 19)
        area_str = spm_unit.household("il_aabd_area", period).decode_to_str()

        # Sum allowances for all applicable utility types
        total_allowance = 0
        for expense in p.utility.utility_types:
            expense_amount = spm_unit(expense, period)
            utility_type = expense.replace("_expense", "")

            # Access parameter using decoded string
            allowance_amount = p.utility[utility_type][area_str][capped_size]

            utility_allowance = where(
                expense_amount > 0,
                min_(expense_amount, allowance_amount),
                0,
            )
            total_allowance += utility_allowance

        return total_allowance
