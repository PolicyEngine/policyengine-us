from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income.medicaid_income_level import (
    medicaid_income_eligible,
)


class is_pregnant_for_medicaid_fc(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid pregnant financial criteria"
    definition_period = YEAR
    reference = (
        # 42 CFR 435.116(b): pregnant women with household income at or below the
        # state's income standard.
        "https://www.law.cornell.edu/cfr/text/42/435.116",
        # WIC § 15832(a)(1)(B): California's Medi-Cal Access Program covers
        # household income "above 208 percent" but "not exceed[ing] 317
        # percent" of the FPL (213% and 322% after the 5 percentage point MAGI
        # disregard), so income exactly at the pregnancy Medi-Cal limit stays in
        # Medi-Cal. The section-level URL returns a version picker; this link
        # renders the full chapter text.
        "https://leginfo.legislature.ca.gov/faces/codes_displayText.xhtml?lawCode=WIC&division=9.&title=&part=3.3.&chapter=2.&article=",
        # R.I. Gen. Laws § 42-12.3-3(g): people eligible for Medicaid or CHIP
        # while pregnant keep full Medicaid through the postpartum period.
        "https://webserver.rilegislature.gov/Statutes/TITLE42/42-12.3/42-12.3-3.htm",
        # 210-RICR-30-00-1 § 1.6(A)(2)(a)(2), insured route from August 17, 2025.
        "https://risos-apa-production-public.s3.amazonaws.com/EOHHS/REG_13314_20250728104245127.pdf#page=5",
        # 1115 Budget Population 6b, insured pregnant women, December 23, 2013
        # to December 31, 2018.
        "https://www.medicaid.gov/Medicaid-CHIP-Program-Information/By-Topics/Waivers/1115/downloads/ri/Comprehensive-Demonstration/ri-global-consumer-choice-compact-expnditure-auth-12232013-12312018.pdf#page=2",
        # 1115 Budget Population 6b, 2019 to 2024 (March 21, 2024 approval).
        "https://www.medicaid.gov/medicaid/section-1115-demonstrations/downloads/ri-comphnsve-dmnstrtn-aprvl.pdf#page=11",
        # 1115 Budget Population 6b, extended through June 30, 2025.
        "https://www.medicaid.gov/medicaid/section-1115-demonstrations/downloads/ri-comphnsve-dmnstrtn-tmp-extn-amndmnt.pdf#page=6",
        # PDF pages 3, 15: 1115 Budget Population 6b, 2026 to 2030.
        "https://www.medicaid.gov/medicaid/section-1115-demonstrations/downloads/ri-comp-demo-appvl-11282025.pdf#page=3",
    )

    def formula(person, period, parameters):
        ma = parameters(period).gov.hhs.medicaid.eligibility.categories.pregnant
        state = person.household("state_code_str", period)
        income_limit = ma.income_limit[state]
        ri_higher_limit = person("ri_medicaid_has_third_party_coverage", period)
        # NOTE: 210-RICR-30-00-1 § 1.6(B) gives one pregnancy row (253% FPL plus
        # the disregard) for insured Medicaid and uninsured CHIP, so this reuses
        # the CHIP pregnancy limit. A CHIP-only change to that parameter would
        # also move Rhode Island's insured Medicaid route.
        chip_income_limit = parameters(period).gov.hhs.chip.pregnant.income_limit[state]
        income_limit = where(ri_higher_limit, chip_income_limit, income_limit)
        # Only a Medicaid pregnancy keeps the pregnancy group (SHO 21-007 Q6).
        coverage = person("ri_pregnancy_coverage", period)
        ri_postpartum_eligible = person(
            "ri_medicaid_postpartum_eligible", period.first_month
        ) & (coverage == coverage.possible_values.MEDICAID)
        return (
            medicaid_income_eligible(person, period, parameters, income_limit)
            | ri_postpartum_eligible
        )
