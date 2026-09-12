from policyengine_us.model_api import *

# Parameter keys that differ from the <type>_expense naming of the
# utility_types entries: the regulation's "metered gas" allowance is paid
# against the household's gas_expense.
PARAMETER_KEY_OVERRIDES = {"gas_expense": "metered_gas"}


class il_aabd_utility_allowance(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois Aid to the Aged, Blind or Disabled (AABD) utility allowance"
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
        allowances = []
        for expense in p.utility.utility_types:
            expense_amount = spm_unit(expense, period)
            key = PARAMETER_KEY_OVERRIDES.get(expense, expense.replace("_expense", ""))
            allowances.append(
                where(
                    expense_amount > 0,
                    min_(expense_amount, p.utility[key][area][capped_size]),
                    0,
                )
            )
        total_allowance = sum(allowances)
        return total_allowance
