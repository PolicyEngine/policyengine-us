from policyengine_us.model_api import *


class msp_part_b_premium_coverage(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Medicare Part B premium amount covered by MSP"
    definition_period = YEAR
    reference = (
        "https://www.medicare.gov/basics/costs/help/medicare-savings-programs",
    )
    documentation = """
    Annual standard Part B premium amount paid on the enrollee's behalf through a
    Medicare Savings Program-like pathway.

    This uses the MSP income and asset rules directly and intentionally avoids the
    modeled Medicaid exclusion used in QI eligibility because that path reaches the
    medically needy Medicaid formula, which depends on medical_out_of_pocket_expenses
    and would create a cycle in SPM MOOP calculations.

    The coverage amount is capped at the standard Part B premium. Any IRMAA amount
    above the standard premium remains the enrollee's responsibility.
    """

    def formula(person, period, parameters):
        first_month = period.first_month
        enrolled = person("medicare_enrolled", period)
        income_eligible = person("msp_income_eligible", first_month)
        asset_eligible = person("msp_asset_eligible", first_month)
        covered_standard_premium = person("base_part_b_premium", period)
        eligible_for_coverage = enrolled & income_eligible & asset_eligible
        return where(eligible_for_coverage, covered_standard_premium, 0)
