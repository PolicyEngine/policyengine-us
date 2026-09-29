from policyengine_us.model_api import *


class ca_fera_eligible(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Eligible for California FERA program"
    documentation = (
        "Eligible for California Family Electric Rate Assistance. PG&E Schedule "
        "E-FERA admits separately metered residences, sub-metered tenants, and "
        "other qualifying applicants in individually metered units, and bars "
        "master-metered customers without sub-metering. As with CARE, the model "
        "uses tenant_pays_utilities as a proxy, which over-excludes PG&E "
        "residents of individually metered units whose landlord holds the "
        "account. FERA discounts electricity only, but the flag covers any "
        "utility, so a household with electricity in rent and its own gas "
        "account still passes."
    )
    reference = (
        "https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/electric-costs/care-fera-program",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PUC&sectionNum=739.12",
        # Applicability and Special Condition 2: separately metered residences
        # and sub-metered tenants; bars master-metered customers without
        # sub-metering.
        "https://www.pge.com/tariffs/assets/pdf/tariffbook/ELEC_SCHEDS_E-FERA.pdf#page=1",
        # Special Condition 3 (certification): other qualifying applicants in
        # individually metered units.
        "https://www.pge.com/tariffs/assets/pdf/tariffbook/ELEC_SCHEDS_E-FERA.pdf#page=2",
    )
    defined_for = StateCode.CA

    def formula(household, period, parameters):
        # Check not eligible for CARE
        care_eligible = household("ca_care_eligible", period)
        # Check the minimum household size
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
        # Check the household pays its own utilities, a proxy for the tariff's
        # metering rules that over-excludes PG&E residents of individually
        # metered units whose landlord holds the account. This gate also keeps
        # a household below the CARE income limit from passing ~care_eligible
        # when CARE is denied only because utilities are included in rent.
        pays_utilities = household("tenant_pays_utilities", period)
        return (
            income_eligible & eligible_household_size & ~care_eligible & pays_utilities
        )
