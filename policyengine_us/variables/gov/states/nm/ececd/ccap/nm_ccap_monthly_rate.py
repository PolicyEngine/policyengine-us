from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.nm.ececd.ccap.nm_ccap_provider_type import (
    NMCCAPProviderType,
)


class nm_ccap_monthly_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = MONTH
    label = "New Mexico CCAP monthly provider reimbursement rate"
    defined_for = "nm_ccap_eligible_child"
    reference = "https://www.nmececd.org/wp-content/uploads/2024/05/Cost-Model-Reimbursement-Rate-Flyer-English-and-Spanish-Revised-May-2024.pdf#page=2"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nm.ececd.ccap
        provider_type = person("nm_ccap_provider_type", period)
        focus_level = person("nm_ccap_focus_level", period)
        age_group = person("nm_ccap_age_group", period)
        service_unit = person("nm_ccap_service_unit", period)

        rates = p.rates
        # Licensed Center / Group Home / Family Home rates vary by FOCUS level
        # and age group; Registered / In-Home receives a single rate by age
        # group with no FOCUS dimension.
        center_rate = rates.center[focus_level][age_group]
        group_home_rate = rates.group_home[focus_level][age_group]
        family_home_rate = rates.family_home[focus_level][age_group]
        registered_rate = rates.registered_home[age_group]
        types = NMCCAPProviderType
        full_time_rate = select(
            [
                provider_type == types.CENTER,
                provider_type == types.GROUP_HOME,
                provider_type == types.FAMILY_HOME,
                provider_type == types.REGISTERED_HOME,
            ],
            [
                center_rate,
                group_home_rate,
                family_home_rate,
                registered_rate,
            ],
            default=registered_rate,
        )
        # Part-time service units pay a fraction of the full-time rate.
        applicable_rate = full_time_rate * rates.service_unit_fraction[service_unit]
        # Non-traditional-hours differential adds a share of the applicable rate.
        non_traditional_hours = person("nm_ccap_non_traditional_hours", period)
        supplement_rate = p.supplements.non_traditional_hours.calc(
            non_traditional_hours
        )
        return applicable_rate * (1 + supplement_rate)
