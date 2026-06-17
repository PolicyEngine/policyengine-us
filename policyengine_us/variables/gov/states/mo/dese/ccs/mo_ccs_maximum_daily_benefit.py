from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.mo.dese.ccs.mo_ccs_provider_type import (
    MOCCSProviderType,
)


class mo_ccs_maximum_daily_benefit(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Missouri Child Care Subsidy maximum daily benefit per child"
    definition_period = MONTH
    defined_for = "mo_ccs_eligible_child"
    reference = "https://dese.mo.gov/sites/dese/files/media/file/2025/12/2025%20Rates%20Held%20Harmless%202.0.xlsx"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mo.dese.ccs
        region = person.household("mo_ccs_region", period.this_year)
        age_group = person("mo_ccs_age_group", period)
        time_category = person("mo_ccs_time_category", period)
        provider_type = person("mo_ccs_provider_type", period)

        rates = p.rates
        # A child with special needs is reimbursed from the special needs (PS)
        # rate column; all other children use the base column. For preschool and
        # school-age children the PS column is the market rate; for
        # infant/toddler the published PS rate equals the base rate (the +25%
        # special-needs enhancement is a deferred follow-up), so special-needs
        # infants reimburse at the base rate.
        is_disabled = person("is_disabled", period.this_year)

        def provider_rate(provider):
            base = provider.base[region][age_group][time_category]
            special_needs = provider.special_needs[region][age_group][time_category]
            return where(is_disabled, special_needs, base)

        return select(
            [
                provider_type == MOCCSProviderType.REGISTERED_CENTER,
                provider_type == MOCCSProviderType.SIX_OR_FEWER,
                provider_type == MOCCSProviderType.LICENSED_CENTER,
                provider_type == MOCCSProviderType.LICENSED_FAMILY_HOME,
                provider_type == MOCCSProviderType.GROUP_HOME,
            ],
            [
                provider_rate(rates.registered_center),
                provider_rate(rates.six_or_fewer),
                provider_rate(rates.licensed_center),
                provider_rate(rates.licensed_family_home),
                provider_rate(rates.group_home),
            ],
        )
