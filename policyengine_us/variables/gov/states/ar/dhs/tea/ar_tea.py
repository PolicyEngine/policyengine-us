from policyengine_us.model_api import *


class ar_tea(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arkansas Transitional Employment Assistance"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/arkansas/208-00-13-Ark-Code-R-SS-001"
    defined_for = "ar_tea_eligible"

    def formula(spm_unit, period, parameters):
        # Per TEA Manual Section 2362 - Reduced Payment - Gross Income Trigger
        p = parameters(period).gov.states.ar.dhs.tea

        maximum_benefit = spm_unit("ar_tea_maximum_benefit", period)
        countable_income = spm_unit("ar_tea_countable_income", period)

        # Check if gross income triggers 50% payment reduction
        gross_income = add(
            spm_unit,
            period,
            ["tanf_gross_earned_income", "tanf_gross_unearned_income"],
        )

        above_trigger = gross_income >= p.payment_standard.trigger.amount
        reduced_payment = maximum_benefit * (
            1 - p.payment_standard.trigger.reduction_rate
        )

        # When gross income >= trigger: payment is 50% of max (no subtraction)
        # When gross income < trigger: payment is max - countable income
        return where(
            above_trigger,
            reduced_payment,
            max_(maximum_benefit - countable_income, 0),
        )
