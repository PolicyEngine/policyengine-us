from policyengine_us.model_api import *


class ar_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arkansas Transitional Employment Assistance (TANF)"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/arkansas/208-00-13-Ark-Code-R-SS-001"
    defined_for = "ar_tanf_eligible"

    def formula(spm_unit, period, parameters):
        # Per 208.00.13 Ark. Code R. Section 001, Section 6.1.1
        p = parameters(period).gov.states.ar.dhs.tanf

        maximum_benefit = spm_unit("ar_tanf_maximum_benefit", period)
        countable_income = spm_unit("ar_tanf_countable_income", period)

        # Check if gross income triggers 50% payment reduction
        gross_earned = spm_unit("tanf_gross_earned_income", period)
        unearned = spm_unit("tanf_gross_unearned_income", period)
        gross_income = gross_earned + unearned

        trigger = p.income.gross_income_trigger
        above_trigger = gross_income >= trigger.amount

        # Apply 50% reduction to maximum payment when above trigger
        effective_maximum = where(
            above_trigger,
            maximum_benefit * (1 - trigger.reduction_rate),
            maximum_benefit,
        )

        return max_(effective_maximum - countable_income, 0)
