from policyengine_us.model_api import *


class wv_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "West Virginia WV Works benefit"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://dhhr.wv.gov/bcf/Services/familyassistance/Pages/WV-WORKS.aspx"
    )
    defined_for = "wv_tanf_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wv.dhhr.wv_works
        # Get household size and cap for lookup
        size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(size, p.max_household_size)
        # Base benefit from payment standard
        payment_standard = p.payment_standard.amount[capped_size]
        # Countable income for benefit reduction
        countable_income = spm_unit("wv_tanf_countable_income", period)
        # Apply benefit reduction rate (60%) to countable income
        income_reduction = countable_income * p.benefit.reduction_rate
        # Count dependent children for child supplement
        dependent_children = spm_unit(
            "spm_unit_count_children", period.this_year
        )
        child_supplement = (
            dependent_children * p.benefit.child_supplement.amount
        )
        # Calculate benefit: Base - reduction + child supplement
        benefit = payment_standard - income_reduction + child_supplement
        return max_(benefit, 0)
