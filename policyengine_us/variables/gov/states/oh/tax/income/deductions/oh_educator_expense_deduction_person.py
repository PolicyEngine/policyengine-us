from policyengine_us.model_api import *


class oh_educator_expense_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "Ohio educator expense deduction"
    unit = USD
    definition_period = YEAR
    default_value = 0
    defined_for = StateCode.OH
    documentation = (
        "Ohio-specific educator deduction allowed in excess of the federal "
        "educator deduction for a qualifying Ohio educator. This remains an "
        "explicit input because the baseline data do not identify Ohio "
        "licensure/teaching status or expenses above the federal deduction."
    )
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01#A_31",  # ORC 5747.01(A)(31): Ohio educator deduction
        "https://dam.assets.ohio.gov/image/upload/v1767095693/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=25",  # 2025 IT-1040 booklet, Ohio educator expense deduction
    )
