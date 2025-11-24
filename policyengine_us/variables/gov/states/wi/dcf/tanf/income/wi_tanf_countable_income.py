from policyengine_us.model_api import *


class wi_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Wisconsin TANF countable income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/03/"
        "03.2.7_Counting_Income.htm",
        "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/03/"
        "03.2.8_DISREGARDING_INCOME.htm",
    )
    defined_for = StateCode.WI
    documentation = """
    Wisconsin W-2 counts all earned and unearned income of W-2 Group
    members with extensive disregards including:
    - All child support (regular collections and arrears)
    - Federal and state EITC
    - Federal income tax refunds
    - All earned income of dependent children
    - SSI payments received by dependent children
    - W-2 program payments (CSJ, W-2 T, CMC, ARP, TEMP)
    - Educational aid (scholarships, loans, grants, work-study)
    - In-kind benefits (meals, clothing, housing)

    For simplified implementation, we use federal gross income baseline
    and apply major disregards that are available in PolicyEngine data.
    """

    def formula(spm_unit, period, parameters):
        # Wisconsin disregards all earned income of dependent children (< 18)
        # Calculate earned income for adults only
        is_adult = spm_unit.members("age", period.this_year) >= 18
        adult_earned = spm_unit.sum(
            spm_unit.members("tanf_gross_earned_income", period) * is_adult
        )

        # All unearned income is counted (including children's)
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])

        # Total gross income (adult earned + all unearned)
        total_income = adult_earned + gross_unearned

        # Wisconsin-specific disregards (implemented where data available)
        # Child support is fully disregarded
        # Note: Child support is already included in tanf_gross_unearned_income,
        # so we subtract it here to implement the disregard
        child_support = add(spm_unit, period, ["child_support_received"])

        # Apply disregards
        # NOTE: Wisconsin disregards many additional income sources that
        # are not separately tracked in PolicyEngine (educational aid,
        # in-kind benefits, SSI for children, EITC, etc.)
        # EITC and other tax credits are NOT included in gross income,
        # so they don't need to be subtracted as disregards.
        disregards = child_support

        return max_(total_income - disregards, 0)
