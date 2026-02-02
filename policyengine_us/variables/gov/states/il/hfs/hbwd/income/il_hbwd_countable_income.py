from policyengine_us.model_api import *


class il_hbwd_countable_income(Variable):
    value_type = float
    unit = USD
    entity = SPMUnit
    label = "Illinois Health Benefits for Workers with Disabilities countable income"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.510",
        "https://hfs.illinois.gov/medicalprograms/hbwd/eligibility.html",
    )
    defined_for = "is_tax_unit_head_or_spouse"

    adds = [
        "il_hbwd_countable_earned_income",
        "il_hbwd_countable_unearned_income",
    ]
    # Per § 120.510(f), count income of individual AND spouse
    # Per § 120.510(i), earned income exemptions apply only to disabled worker
    # Adds automatically sums across SPM unit members
