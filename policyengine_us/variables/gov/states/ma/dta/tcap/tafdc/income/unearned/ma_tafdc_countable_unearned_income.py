from policyengine_us.model_api import *


class ma_tafdc_countable_unearned_income(Variable):
    value_type = float
    unit = USD
    entity = SPMUnit
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) countable unearned income"
    definition_period = MONTH
    reference = (
        "https://www.masslegalservices.org/content/62-what-income-counted"
    )
    defined_for = StateCode.MA

    def formula(spm_unit, period, parameters):
        total_unearned_income = add(
            spm_unit, period, ["ma_tcap_gross_unearned_income"]
        )
        child_support_deduction = add(
            spm_unit, period, ["ma_tafdc_child_support_deduction"]
        )
        return max_(0, total_unearned_income - child_support_deduction)
