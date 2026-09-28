from policyengine_us.model_api import *


class ca_care_eligible(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Eligible for California CARE program"
    documentation = (
        "Eligible for California Alternate Rates for Energy, an on-bill "
        "discount. SDG&E limits applicants to the utility's customer of record "
        "or a sub-metered tenant; PG&E also admits any permanent resident of an "
        "individually metered unit. Both tariffs exclude non-sub-metered "
        "tenants of master-metered customers. The model has no utility-territory "
        "or metering input, so a household with utilities included in rent "
        "(tenant_pays_utilities false) is treated as ineligible. That matches "
        "SDG&E but over-excludes PG&E residents of individually metered units "
        "whose landlord holds the account."
    )
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PUC&sectionNum=739.1",
        # Sub-metered tenants of a master-meter customer remain eligible.
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PUC&sectionNum=739.5",
        # Rule 19.1 A: admits permanent residents of individually metered units
        # but excludes non-sub-metered tenants of master-metered customers.
        "https://www.pge.com/tariffs/assets/pdf/tariffbook/ELEC_RULES_19.1.pdf#page=1",
        # E-CARE Special Condition 4: customer of record or sub-metered tenant.
        "https://www.sdge.com/sites/default/files/elec_elec-scheds_e-care.pdf#page=3",
    )
    defined_for = StateCode.CA

    def formula(household, period, parameters):
        categorically_eligible = household("ca_care_categorically_eligible", period)
        income_eligible = household("ca_care_income_eligible", period)
        pays_utilities = household("tenant_pays_utilities", period)
        return (categorically_eligible | income_eligible) & pays_utilities
