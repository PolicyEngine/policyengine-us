from policyengine_us.model_api import *


class is_chip_fcep_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Pregnant person eligible for CHIP through the FCEP option"
    documentation = (
        "Determines whether a pregnant person is eligible for the Children's "
        "Health Insurance Program through the From-Conception-to-End-of-"
        "Pregnancy option. This is modeled as a pregnant-person proxy because "
        "PolicyEngine-US does not represent unborn-child entities."
    )
    definition_period = YEAR
    reference = (
        # CMS: the FCEP option covers the unborn child from conception to end of
        # pregnancy "regardless of their parent's citizenship or immigration status."
        "https://www.medicaid.gov/chip/chip-eligibility-enrollment",
        # 42 CFR 457.10 defines "child" to include the period from conception to
        # birth, so the unborn child (not the parent) is the CHIP beneficiary.
        "https://www.law.cornell.edu/cfr/text/42/457.10",
        "https://www.kff.org/affordable-care-act/state-indicator/medicaid-and-chip-income-eligibility-limits-for-pregnant-women-as-a-percent-of-the-federal-poverty-level",
    )

    def formula(person, period, parameters):
        # Get state code
        state_code = person.household("state_code", period)

        # Check pregnancy status
        is_pregnant = person("is_pregnant", period)

        # Check if state offers the FCEP option
        p = parameters(period).gov.hhs.chip.fcep
        income_limit = p.income_limit[state_code]

        state_has_fcep = income_limit > 0

        # Alabama phased in its FCEP coverage ("ALL Babies") by county before
        # extending it statewide, so it is the only state whose FCEP coverage is
        # geographically limited. Every other state that offers FCEP covers its
        # whole territory, so the county gate only applies within Alabama.
        in_alabama = state_code == StateCode.AL
        alabama_statewide = p.al_statewide
        county = person.household("county_str", period)
        in_alabama_fcep_county = np.isin(county, p.al_counties)
        # Households with an UNKNOWN county still qualify once coverage is
        # statewide; before then they must fall in a covered county.
        alabama_geographic_eligible = alabama_statewide | in_alabama_fcep_county
        fcep_geographic_eligible = ~in_alabama | alabama_geographic_eligible

        # The parent's immigration status is not tested: under the FCEP option the
        # unborn child is the CHIP beneficiary, and CMS provides prenatal and
        # pregnancy-related benefits regardless of the parent's citizenship or
        # immigration status (42 CFR 457.10).

        # Check income eligibility
        # CHIP is for pregnant women who make too much for Medicaid but below CHIP limits
        # First, check if not eligible for Medicaid
        medicaid_eligible = person("is_medicaid_eligible", period)

        # Check if family income is below CHIP threshold
        # Use medicaid_income_level as the income measure
        income_ratio = person("medicaid_income_level", period)
        income_eligible = income_ratio <= income_limit

        return (
            is_pregnant
            & state_has_fcep
            & fcep_geographic_eligible
            & ~medicaid_eligible
            & income_eligible
        )
