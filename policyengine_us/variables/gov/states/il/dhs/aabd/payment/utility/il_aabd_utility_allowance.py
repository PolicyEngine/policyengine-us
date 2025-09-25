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
        area = spm_unit.household("il_aabd_area", period)
        # Households may have more than one applicable utility allowance type
        total_allowance = sum(
            [
                where(
                    spm_unit(expense, period) > 0,
                    min(
                        spm_unit(expense, period),
                        p.utility[expense.replace("_expense", "")][area][
                            capped_size
                        ],
                    ),
                    0,
                )
                for expense in p.utility.utility_types
            ]
        )
        return total_allowance
