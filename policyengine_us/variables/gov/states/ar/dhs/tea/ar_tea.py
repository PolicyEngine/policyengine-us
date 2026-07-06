from policyengine_us.model_api import *


class ar_tea(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arkansas Transitional Employment Assistance"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/arkansas/208-00-13-Ark-Code-R-SS-001"
    )
    defined_for = "ar_tea_eligible"

    def formula(spm_unit, period, parameters):
        # Per TEA Policy Manual Section 2362 - Reduced Payment - Gross Income
        # Trigger (effective 01/01/2023). Income eligibility (countable income
        # <= $513) is already enforced by ar_tea_eligible, so a family reaching
        # this formula is income eligible. The payment is a flat grant, not a
        # gap-filled benefit: it is the full maximum grant for the family size
        # when gross income is below the trigger, and 50% of that maximum when
        # gross income is at or above the trigger. Countable income is never
        # subtracted from the grant (Section 2362 Example #1: $150 gross income
        # yields the full $204 grant for a family of three).
        p = parameters(period).gov.states.ar.dhs.tea

        maximum_benefit = spm_unit("ar_tea_maximum_benefit", period)

        # Countable monthly gross income, excluding assigned child support.
        gross_income = add(
            spm_unit,
            period,
            ["tanf_gross_earned_income", "tanf_gross_unearned_income"],
        )

        # When gross income >= trigger: payment reduced by 50% of the maximum.
        # When gross income < trigger: payment is the full maximum grant.
        above_trigger = gross_income >= p.payment_standard.trigger.amount
        reduced_payment = maximum_benefit * (
            1 - p.payment_standard.trigger.reduction_rate
        )
        return where(
            above_trigger,
            reduced_payment,
            maximum_benefit,
        )
