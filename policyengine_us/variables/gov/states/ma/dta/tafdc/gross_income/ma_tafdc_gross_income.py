from policyengine_us.model_api import *


class ma_tafdc_gross_income(Variable):
    value_type = float
    unit = USD
    entity = SPMUnit
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) gross income"
    definition_period = YEAR
    reference = "https://www.masslegalservices.org/content/73-how-much-income-can-you-have-and-still-qualify-tafdc"
    defined_for = StateCode.MA

    def formula(spm_unit, period, parameters):
        is_grandparent = spm_unit.members(
            "is_grandparent_of_filer_or_spouse", period
        )
        total_income = (
            add(
                spm_unit,
                period,
                ["ma_tafdc_earned_income", "ma_tafdc_unearned_income"],
            )
            * ~is_grandparent
        )
        grandparent_income = spm_unit(
            "ma_tafdc_grandparent_gross_income", period
        )
        return total_income + grandparent_income
