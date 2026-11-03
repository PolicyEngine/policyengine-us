from policyengine_us.model_api import *


class az_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for Arizona LIHEAP"
    documentation = (
        "Arizona household with at least one citizen or qualified noncitizen "
        "member that is categorically or income eligible, has a counted energy "
        "bill or energy included in its rent, and reports its heating fuel. The "
        "subsidized-housing utility allowance test, the Tribal LIHEAP "
        "first-apply rule and the bar on costs already paid by another program "
        "have no inputs and are not modeled."
    )
    reference = (
        # PDF pages 4-8, 33
        "https://des.az.gov/sites/default/files/dl/CCSD-LIHEAP-Policy.pdf#page=4",
        "https://liheapch.acf.gov/docs/2026/state-plans/AZ_Plan_2026.pdf#page=9",
    )
    defined_for = StateCode.AZ

    def formula(spm_unit, period, parameters):
        # Section VI.A.3: "An Applicant, or a Household member, must be an
        # Eligible Household Member"; the size counts only such members.
        has_eligible_member = spm_unit("az_liheap_household_size", period) > 0
        # Section VI.A.6.a: "A Household must either meet Categorical
        # Eligibility or Income Eligibility requirements."
        categorically_eligible = spm_unit("az_liheap_categorically_eligible", period)
        income_eligible = spm_unit("az_liheap_income_eligible", period)
        # Section VI.A.1: "An Applicant must require assistance with payment of
        # energy-related expenses." The Household definition (page 5) includes
        # members "who make undesignated payments for Energy Utilities in the
        # form of rent", and Section VII.B.3.a.ii.B pays the applicant directly
        # when "Energy Utilities are included within the cost of their rent".
        has_energy_cost = spm_unit("az_liheap_energy_cost", period) > 0
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        # heating_type is a required input and UNSPECIFIED pays nothing. NONE
        # stays eligible: the Standard benefit pays any heating or cooling
        # Energy Utility bill, not the heating fuel alone, so a home without
        # heating that pays for electricity still requires assistance.
        heating_type = spm_unit("heating_type", period)
        known_fuel = heating_type != heating_type.possible_values.UNSPECIFIED
        return (
            has_eligible_member
            & (categorically_eligible | income_eligible)
            & (has_energy_cost | heat_in_rent)
            & known_fuel
        )
