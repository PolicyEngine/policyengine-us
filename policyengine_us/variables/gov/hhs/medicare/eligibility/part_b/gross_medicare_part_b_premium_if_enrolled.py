from policyengine_us.model_api import *


class gross_medicare_part_b_premium_if_enrolled(Variable):
    value_type = float
    entity = Person
    label = "Gross Medicare Part B premium if enrolled"
    unit = USD
    definition_period = YEAR
    defined_for = "medicare_enrolled"
    reference = "https://www.medicare.gov/your-medicare-costs/part-b-costs"
    documentation = (
        "Annual Medicare Part B premium for enrolled beneficiaries before "
        "Medicare Savings Program coverage, including any income-related "
        "monthly adjustment amount. Use this enrollment-gated gross premium "
        "for CMS premiums-from-enrollees calibration targets."
    )

    def formula(person, period, parameters):
        return person("gross_medicare_part_b_premium", period)
