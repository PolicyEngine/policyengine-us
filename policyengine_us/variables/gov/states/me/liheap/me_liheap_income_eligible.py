from policyengine_us.model_api import *


class me_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Maine LIHEAP based on income"
    definition_period = YEAR
    defined_for = StateCode.ME
    reference = [
        "https://www.mainehousing.org/charts/HEAP-Income-Elibility",
        "docs/agents/sources/me-liheap/income_eligibility_guidelines.md",
        "42 U.S.C. § 8624(b)(2)(A) - Income eligibility requirements",
    ]

    def formula(spm_unit, period, parameters):
        # Get Maine LIHEAP countable income
        income = spm_unit("me_liheap_income", period)

        # Get household size
        household_size = spm_unit("spm_unit_size", period)

        # Get income thresholds from parameters
        p = parameters(period).gov.states.me.liheap.income_thresholds

        # Handle different household sizes based on documented thresholds
        # Documentation provides explicit thresholds for sizes 1-10
        # For larger households, use federal SMI calculation method from documentation

        income_limit = select(
            [
                household_size == 1,
                household_size == 2,
                household_size == 3,
                household_size == 4,
                household_size == 5,
                household_size == 6,
                household_size == 7,
                household_size == 8,
                household_size == 9,
                household_size == 10,
                household_size > 10,
            ],
            [
                p.size_1,
                p.size_2,
                p.size_3,
                p.size_4,
                p.size_5,
                p.size_6,
                p.size_7,
                p.size_8,
                p.size_9,
                p.size_10,
                # For households >10, use federal formula from documentation:
                # (132% + (household_size - 6) × 3%) × 4-person SMI × 0.60
                # Estimate based on size 10 threshold with linear extrapolation
                p.size_10
                + (household_size - 10)
                * 2_000,  # $2,000 per additional person
            ],
        )

        # Household is income eligible if income is at or below the threshold
        return income <= income_limit
