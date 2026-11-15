from policyengine_us.model_api import *


class msp_part_b_premium_coverage(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Medicare Part B premium amount covered by MSP"
    definition_period = YEAR
    reference = (
        "https://www.medicare.gov/basics/costs/help/medicare-savings-programs",
        "https://www.law.cornell.edu/uscode/text/42/1396b#v",
        "https://www.law.cornell.edu/uscode/text/8/1613#a",
    )
    documentation = """
    Annual standard Part B premium amount paid on the enrollee's behalf through a
    Medicare Savings Program-like pathway.

    This uses the MSP income and asset rules and
    is_federal_medicaid_immigration_status_eligible directly and intentionally avoids
    the modeled Medicaid exclusion used in QI eligibility because that path reaches the
    medically needy Medicaid formula, which depends on medical_out_of_pocket_expenses
    and would create a cycle in SPM MOOP calculations.

    The coverage amount is capped at the standard Part B premium. Any IRMAA amount
    above the standard premium remains the enrollee's responsibility.
    """

    def formula(person, period, parameters):
        enrolled = person("medicare_enrolled", period)
        monthly_standard_premium = (
            person("base_part_b_premium", period) / MONTHS_IN_YEAR
        )
        # MSP coverage is a federal Medicaid benefit, so the federal Medicaid
        # immigration test (42 U.S.C. 1396b(v), 8 U.S.C. 1611(a) and 1613(a))
        # applies. State-funded Medicaid coverage does not open it.
        immigration_eligible = person(
            "is_federal_medicaid_immigration_status_eligible", period
        )
        monthly_coverage = 0
        for month in period.get_subperiods(MONTH):
            income_eligible = person("msp_income_eligible", month)
            asset_eligible = person("msp_asset_eligible", month)
            eligible_for_coverage = (
                enrolled & income_eligible & asset_eligible & immigration_eligible
            )
            monthly_coverage += where(
                eligible_for_coverage,
                monthly_standard_premium,
                0,
            )
        return monthly_coverage
