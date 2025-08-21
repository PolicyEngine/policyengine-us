from policyengine_us.model_api import *


class ny_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for New York State LIHEAP"
    definition_period = YEAR
    defined_for = StateCode.NY
    reference = (
        "https://otda.ny.gov/programs/heap/",
        "https://liheapch.acf.gov/tables/liheap/FY2025SMI/FY25smi.htm",
    )
    documentation = "Uses 60% of State Median Income as income limit per federal LIHEAP regulations"

    def formula(spm_unit, period, parameters):
        # NY HEAP program year starts November 2024
        if period.start.year < 2025:
            return False

        p = parameters(period).gov.states.ny.otda.liheap

        # Check immigration status - at least one member must be eligible
        immigration_eligible = spm_unit.any(
            "ny_liheap_immigration_eligible", period
        )

        # The income concept is not clearly defined, assuming IRS gross income
        income = add(spm_unit, period, ["irs_gross_income"])

        # NY uses 60% SMI for most households, 150% FPG for large households
        household_size = spm_unit("spm_unit_size", period)
        state_median_income = spm_unit("hhs_smi", period)
        fpl = spm_unit("spm_unit_fpg", period)

        # For large households, use FPG; otherwise use SMI
        income_limit = where(
            household_size >= p.large_household_size,
            fpl * p.fpg_limit,  # 150% FPG
            state_median_income * p.smi_limit,  # 60% SMI
        )

        # Check categorical eligibility through other programs
        categorically_eligible = (
            add(spm_unit, period, p.categorical_eligibility) > 0
        )

        # Must meet immigration status AND (income OR categorical eligibility)
        return immigration_eligible & ((income <= income_limit) | categorically_eligible)
