from policyengine_us.model_api import *


class oh_educator_expense_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "Ohio educator expense deduction"
    unit = USD
    definition_period = YEAR
    default_value = 0
    defined_for = StateCode.OH
    # ORC § 5747.01(A)(31): Ohio allows a deduction ONLY for educator
    # expenses in EXCESS of the federal IRC § 62(a)(2)(D) cap (currently
    # $300). The federal-cap portion is already deducted via federal AGI;
    # adding the federal `educator_expense` here would double-count. This
    # stub variable therefore replaces (not supplements) the federal
    # educator deduction in oh/.../deductions.yaml. It remains an explicit
    # input because the baseline data do not identify Ohio licensure or
    # the excess-over-federal amount; filers without microdata input
    # receive 0, which matches the federal cap behavior.
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01#A_31",  # ORC 5747.01(A)(31): Ohio educator deduction
        "https://dam.assets.ohio.gov/image/upload/v1767095693/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=25",  # 2025 IT-1040 booklet, Ohio educator expense deduction
    )
