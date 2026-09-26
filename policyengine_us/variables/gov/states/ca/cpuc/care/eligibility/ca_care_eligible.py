from policyengine_us.model_api import *


class ca_care_eligible(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Eligible for California CARE program"
    documentation = (
        "Eligible for California Alternate Rates for Energy. CARE is an on-bill "
        "discount for the utility customer or a sub-metered tenant; the tariff "
        "excludes non-sub-metered tenants of master-metered customers. The "
        "model has no metering input, so a household whose utilities are "
        "included in rent (tenant_pays_utilities false) is treated as such a "
        "tenant."
    )
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PUC&sectionNum=739.1",
        # Sub-metered tenants of a master-meter customer remain eligible.
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PUC&sectionNum=739.5",
        # Excludes non-sub-metered tenants of master-metered customers.
        "https://www.pge.com/tariffs/assets/pdf/tariffbook/ELEC_RULES_19.1.pdf#page=1",
    )
    defined_for = StateCode.CA

    def formula(household, period, parameters):
        categorically_eligible = household("ca_care_categorically_eligible", period)
        income_eligible = household("ca_care_income_eligible", period)
        pays_utilities = household("tenant_pays_utilities", period)
        return (categorically_eligible | income_eligible) & pays_utilities
