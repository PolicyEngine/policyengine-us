from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.id.dhw.iccp.id_iccp_provider_type import (
    IDICCPProviderType,
)


class id_iccp_maximum_monthly_benefit(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = MONTH
    label = "Idaho Child Care Program maximum monthly benefit per child"
    defined_for = "id_iccp_eligible_child"
    reference = (
        "https://adminrules.idaho.gov/rules/current/16/160612.pdf#page=15",
        "https://publicdocuments.dhw.idaho.gov/WebLink/DocView.aspx?dbid=0&id=19508&repo=PUBLIC-DOCUMENTS#page=1",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.id.dhw.iccp.rates
        cluster = person.household("id_iccp_county_cluster", period.this_year)
        time_category = person("id_iccp_time_category", period)
        age_group = person("id_iccp_age_group", period)
        provider_type = person("id_iccp_provider_type", period)
        in_care = person("childcare_hours_per_week", period.this_year) > 0
        rate = where(
            provider_type == IDICCPProviderType.CENTER,
            p.center[cluster][time_category][age_group],
            p.family[cluster][time_category][age_group],
        )
        return where(in_care, rate, 0)
