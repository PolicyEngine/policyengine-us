from policyengine_us.model_api import *


class il_aabd_utility_allowance(Variable):
    value_type = float
    entity = Person
    label = (
        "Illinois Aid to the Aged, Blind or Disabled (AABD) utility allowance"
    )
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.IL
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.259",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.dhs.aabd.payment
        size = person.spm_unit("spm_unit_size", period)
        capped_size = clip(size, 1, 19)
        area = person.household("il_aabd_area", period)
        expense_types = p.utility.utility_types
        sum_of_allowances = sum(
            [
                p.utility[expense.replace("_expense", "")][area][capped_size]
                for expense in expense_types
            ]
        )  # a household may not have all of the expenses, at this point, I summed all of them

        return sum_of_allowances
