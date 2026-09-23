from policyengine_us.model_api import *


class ca_fera_eligible(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Eligible for California FERA program"
    documentation = "Eligible for California Alternate Rates for Energy"
    reference = (
        "https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/electric-costs/care-fera-program",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PUC&sectionNum=739.12",
        # Applies to separately metered residences and sub-metered tenants.
        "https://www.pge.com/tariffs/assets/pdf/tariffbook/ELEC_SCHEDS_E-FERA.pdf#page=1",
    )
    defined_for = StateCode.CA

    def formula(household, period, parameters):
        # Check not eligible for CARE
        care_eligible = household("ca_care_eligible", period)
        # Check at least 3 people in household
        n = household("household_size", period)
        p = parameters(period).gov.states.ca.cpuc.fera.eligibility
        eligible_household_size = n >= p.minimum_household_size
        # Check income eligibility with respect to percent of the poverty line.
        # Must be above 200% of the poverty line (CARE requirements), but less
        # than or equal to 250% of the poverty line.
        income = household("ca_cpuc_countable_income", period)
        ca_care_poverty_line = household("ca_care_poverty_line", period)
        income_limit = ca_care_poverty_line * p.fpl_limit
        income_eligible = income <= income_limit
        # Check the household pays its own utilities. This gate also keeps a
        # household below the CARE income limit from passing ~care_eligible
        # when CARE is denied only because utilities are included in rent.
        pays_utilities = household("tenant_pays_utilities", period)
        return (
            income_eligible & eligible_household_size & ~care_eligible & pays_utilities
        )
