from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income.medicaid_income_level import (
    medicaid_income_eligible,
)


class is_chip_eligible_standard_pregnant_person(Variable):
    value_type = bool
    entity = Person
    label = "Pregnant or postpartum person eligible for standard CHIP"
    documentation = (
        "Determines if a pregnant or postpartum person is eligible for the "
        "standard Children's Health Insurance Program, including Rhode "
        "Island's continuous postpartum coverage at the annual model's "
        "January snapshot."
    )
    definition_period = YEAR
    reference = (
        "https://www.ssa.gov/OP_Home/ssact/title21/2110.htm",
        "https://www.law.cornell.edu/uscode/text/42/1397ll#d_2_A",
        "https://www.law.cornell.edu/uscode/text/42/1397gg#e_1_K",
        # PDF pages 2, 4, 7
        "https://www.medicaid.gov/federal-policy-guidance/downloads/sho21007.pdf#page=2",
        "https://www.medicaid.gov/medicaid/national-medicaid-chip-program-information/medicaid-childrens-health-insurance-program-basic-health-program-eligibility-levels",
        "https://www.law.cornell.edu/uscode/text/42/1397ll#d_2_C",
        "https://www.law.cornell.edu/uscode/text/8/1611#a",
        "https://www.law.cornell.edu/uscode/text/8/1641#b",
        "https://www.law.cornell.edu/cfr/text/45/155.20",
        "https://www.medicaid.gov/federal-policy-guidance/downloads/sho-12-002.pdf",
        "https://www.medicaid.gov/federal-policy-guidance/downloads/sho26001.pdf#page=28",
        # 210-RICR-30-00-1 § 1.6(A)(2)(b), version effective August 17, 2025.
        "https://risos-apa-production-public.s3.amazonaws.com/EOHHS/REG_13314_20250728104245127.pdf#page=5",
        "https://www.medicaid.gov/CHIP/Downloads/RI-22-0025.pdf#page=4",
    )

    def formula(person, period, parameters):
        # Get state code
        state_code = person.household("state_code", period)

        # Targeted low-income pregnant women stay eligible through the 60-day
        # postpartum period (42 USC 1397ll(d)(2)(A)). A state that extends
        # Medicaid postpartum coverage to 12 months extends its separate CHIP
        # too (42 USC 1397gg(e)(1)(K); New Jersey and Virginia did both through
        # section 1115 demonstrations), so CHIP reuses the Medicaid
        # non-financial test and its per-state postpartum period.
        is_pregnant_or_postpartum = person("is_pregnant_for_medicaid_nfc", period)

        # Check if state offers CHIP program for pregnant women
        p = parameters(period).gov.hhs.chip.pregnant
        income_limit = p.income_limit[state_code]

        state_has_pregnant_chip = income_limit > 0

        # Check immigration status eligibility
        immigration_eligible = person("is_chip_immigration_status_eligible", period)

        # Check income eligibility
        # CHIP is for pregnant women who make too much for Medicaid but below CHIP limits
        # First, check if not eligible for Medicaid
        medicaid_eligible = person("is_medicaid_eligible", period)

        # Check if family income is below CHIP threshold
        income_eligible = medicaid_income_eligible(
            person, period, parameters, income_limit
        )

        # A targeted low-income pregnant woman must not be covered under a
        # group health plan or health insurance coverage, in the same manner
        # as a child (42 USC 1397ll(d)(2)(C) and 1397jj(b)(1)(C)).
        has_disqualifying_coverage = person(
            "has_chip_disqualifying_health_coverage", period
        )
        # 210-RICR-30-00-1 § 1.6(A)(2)(a)(2), (b): Medicaid and CHIP use the
        # same third-party list in Rhode Island.
        has_disqualifying_coverage = where(
            state_code == StateCode.RI,
            person("ri_medicaid_has_third_party_coverage", period),
            has_disqualifying_coverage,
        )

        return (
            is_pregnant_or_postpartum
            & state_has_pregnant_chip
            & immigration_eligible
            & ~medicaid_eligible
            & income_eligible
            & ~has_disqualifying_coverage
        ) | person("ri_chip_postpartum_eligible", period.first_month)
