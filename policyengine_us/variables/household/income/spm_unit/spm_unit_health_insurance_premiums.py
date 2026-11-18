from policyengine_us.model_api import *


class spm_unit_health_insurance_premiums(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit health insurance premiums"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www2.census.gov/programs-surveys/supplemental-poverty-measure/datasets/spm/spm_techdoc.pdf#page=18",
        "https://www2.census.gov/library/working-papers/2026/adrm/cbsm/rsm2026-04.pdf#page=65",
    )
    documentation = (
        "Health insurance premium expenses for an SPM unit, combining a "
        "data-imputed other premium component with modeled premium components "
        "that can respond to policy reforms, including Medicare Part A and "
        "Part B premiums and the Part D IRMAA surcharge paid out of pocket. "
        "Includes employee-paid pretax payroll premiums in addition to the "
        "disjoint non-pretax premium components; excludes employer contributions."
    )

    adds = [
        "pre_tax_health_insurance_premiums",
        "other_health_insurance_premiums",
        "chip_premium",
        "medicaid_premium",
        "marketplace_net_premium",
        "medicare_part_a_premium",
        "medicare_part_b_premium",
        "income_adjusted_part_d_premium_surcharge",
    ]
