from policyengine_us.model_api import *


class de_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware personal income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenuefiles.delaware.gov/2025/PITForms_Instructions/Instructions/PIT-RES_Instructions_2025-01.pdf#page=5",
        "https://revenuefiles.delaware.gov/2025/PITForms_Instructions/Instructions/PIT-RES_Instructions_2025-01.pdf#page=10",
    )
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        # The joint and combined separate (FS4) paths are computed in full,
        # each after its own non-refundable credits, and the filer takes
        # whichever filing status produces the lower liability. The election
        # itself lives in de_files_separately, which compares the same two
        # post-credit amounts (issue #7931).
        files_separately = tax_unit("de_files_separately", period)
        separate_result = tax_unit(
            "de_income_tax_before_refundable_credits_separate", period
        )
        joint_result = tax_unit("de_income_tax_before_refundable_credits_joint", period)
        return where(files_separately, separate_result, joint_result)
