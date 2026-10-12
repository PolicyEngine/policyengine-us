from policyengine_us.model_api import *


class msp_part_a_premium_coverage(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Medicare Part A premium amount covered by MSP"
    definition_period = YEAR
    reference = (
        "https://www.medicare.gov/basics/costs/help/medicare-savings-programs",
        "https://www.law.cornell.edu/uscode/text/42/1396d#p_3",
    )
    documentation = """
    Annual Part A premium amount paid on the enrollee's behalf through
    Qualified Medicare Beneficiary coverage.

    This gates on QMB rather than the broader MSP income/asset test used by
    msp_part_b_premium_coverage because only QMB pays Part A premiums under
    42 U.S.C. 1396d(p)(3)(A)(i); SLMB and QI cover the Part B premium only.

    The QMB gate is cycle-safe for SPM MOOP: is_qmb_eligible composes
    msp_countable_income (SSI methodology), msp_asset_eligible, and
    is_medicare_eligible directly, without the modeled Medicaid exclusion
    used in QI eligibility that reaches the medically needy Medicaid
    formula and its medical_out_of_pocket_expenses dependency.
    """

    def formula(person, period, parameters):
        enrolled = person("medicare_enrolled", period)
        monthly_part_a_premium = person("base_part_a_premium", period) / MONTHS_IN_YEAR
        monthly_coverage = 0
        for month in period.get_subperiods(MONTH):
            qmb_eligible = person("is_qmb_eligible", month)
            monthly_coverage += where(
                enrolled & qmb_eligible,
                monthly_part_a_premium,
                0,
            )
        return monthly_coverage
