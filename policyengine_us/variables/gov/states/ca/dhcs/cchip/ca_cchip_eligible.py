from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income.medicaid_income_level import (
    medicaid_income_eligible,
)


class ca_cchip_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the California County Children's Health Initiative Program"
    definition_period = YEAR
    reference = (
        # WIC § 15853(a)(1): Title XXI immigration rules, family income at or
        # below 317 percent of the FPL before MAGI conversion, and no eligibility
        # for the optional targeted low-income children group, the Medi-Cal
        # Access Program, or no-cost Medi-Cal.
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=15853.",
        # WIC § 15850.1(d): a child is a person under 19 years of age.
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=15850.1.",
        # CHIP state plan: Population 1/CCHIP, age 0 up to 19, above 261 up to
        # and including 317 percent of the FPL, three counties.
        "https://www.dhcs.ca.gov/wp-content/uploads/2025/10/SPA-24-0012-Approval.pdf#page=23",
        "https://stgenssa.sccgov.org/debs/program_handbooks/medi-cal/assets/35StCtyAdminHealthIns/CCHIP.htm",
        "https://www.medicaid.gov/federal-policy-guidance/downloads/sho-12-002.pdf#page=1",
    )
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.dhcs.cchip
        county = person.household("county_str", period)
        in_cchip_county = np.isin(county, p.counties)
        # WIC § 15850.1(d) and the state plan cover children "from age 0 up to
        # age 19", the federal CHIP definition of a child.
        age = person("age", period)
        age_eligible = age < parameters(period).gov.hhs.chip.child.max_age
        istatus = person("immigration_status", period)
        undocumented = istatus == istatus.possible_values.UNDOCUMENTED
        # California elected the CHIPRA section 214 lawfully residing option for
        # children (state plan section 4.1-LR). CMS SHO #12-002 excludes DACA
        # from that option, and SHO #26-001 leaves the option intact under the
        # October 2026 federal funding limits.
        daca = istatus == istatus.possible_values.DACA
        immigration_eligible = ~(undocumented | daca)
        # WIC § 15853(a)(1)(A)-(B): the child must not qualify for the optional
        # targeted low-income children group or no-cost Medi-Cal, so the 266
        # percent FPL Medi-Cal child limit is the CCHIP floor.
        medicaid_eligible = person("is_medicaid_eligible", period)
        income_eligible = medicaid_income_eligible(
            person, period, parameters, p.income_limit
        )
        has_disqualifying_coverage = person(
            "has_chip_disqualifying_health_coverage", period
        )
        # The county handbook also excludes children with employer coverage
        # available, with no affordability test; the ACA affordable offer input
        # is the closest available proxy.
        offered_esi = person("offered_aca_disqualifying_esi", period)
        return (
            in_cchip_county
            & age_eligible
            & immigration_eligible
            & ~medicaid_eligible
            & income_eligible
            & ~has_disqualifying_coverage
            & ~offered_esi
        )
