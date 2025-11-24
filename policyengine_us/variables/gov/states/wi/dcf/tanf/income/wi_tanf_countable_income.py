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
        # Use federal baseline for gross income
        gross_earned = spm_unit("tanf_gross_earned_income", period)
        gross_unearned = spm_unit("tanf_gross_unearned_income", period)

        # Wisconsin-specific disregards (implemented where data available)
        # Child support is fully disregarded
        child_support = spm_unit("child_support_received", period)

        # EITC is fully disregarded (both federal and state)
        eitc = spm_unit("eitc", period)
        wi_eitc = spm_unit("wi_earned_income_credit", period)

        # Total gross income
        total_income = gross_earned + gross_unearned

        # Apply disregards
        # NOTE: Wisconsin disregards many additional income sources that
        # are not separately tracked in PolicyEngine (educational aid,
        # in-kind benefits, dependent children's income, etc.)
        # This implementation includes major disregards available in data
        disregards = child_support + eitc + wi_eitc

        return max_(total_income - disregards, 0)
