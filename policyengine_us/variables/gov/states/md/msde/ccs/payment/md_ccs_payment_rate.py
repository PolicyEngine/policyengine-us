from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.md.msde.ccs.md_ccs_provider_type import (
    MDCCSProviderType,
)


class md_ccs_payment_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Maryland Child Care Scholarship (CCS) weekly payment rate"
    definition_period = MONTH
    defined_for = "md_ccs_eligible_child"
    reference = "https://earlychildhood.marylandpublicschools.org/families/child-care-scholarship-program/child-care-scholarship-rates"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.md.msde.ccs.payment
        provider_type = person("md_ccs_provider_type", period)
        age_group = person("md_ccs_age_group", period)
        service_unit = person("md_ccs_service_unit", period)
        region = person.household("md_ccs_region", period)

        # Formal rates: by region, age group, and service unit
        center_rate = p.formal.licensed_center[region][age_group][service_unit]
        family_rate = p.formal.licensed_family[region][age_group][service_unit]

        # Informal rates: by county, age group, and service unit
        county = person.household("county_str", period)
        in_md = person.household("state_code_str", period) == "MD"
        safe_county = where(in_md, county, "ALLEGANY_COUNTY_MD")
        informal_rate = p.informal.rates[safe_county][age_group][service_unit]

        return select(
            [
                provider_type == MDCCSProviderType.LICENSED_CENTER,
                provider_type == MDCCSProviderType.LICENSED_FAMILY,
                provider_type == MDCCSProviderType.INFORMAL,
                provider_type == MDCCSProviderType.NONE,
            ],
            [center_rate, family_rate, informal_rate, 0],
        )
