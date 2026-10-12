from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.mi.mdhhs.ccap.mi_ccap_provider_type import (
    MICCAPProviderType,
)


class mi_ccap_hourly_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Michigan CDC department hourly rate per child"
    definition_period = MONTH
    defined_for = "mi_ccap_eligible_child"
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/RF/Public/RFT/270.pdf#page=4"
    )

    def formula(person, period, parameters):
        # RFT 270 Table 2: the department hourly rate is looked up by provider
        # type, star/quality level, and age group.
        p = parameters(period).gov.states.mi.mdhhs.ccap.rates
        provider_type = person("mi_ccap_provider_type", period)
        age_group = person("mi_ccap_age_group", period)
        star_rating = person("mi_ccap_star_rating", period)
        exempt_level = person("mi_ccap_exempt_level", period)

        center_rate = p.center[star_rating][age_group]
        family_home_rate = p.family_home[star_rating][age_group]
        exempt_rate = p.exempt[exempt_level][age_group]

        return select(
            [
                provider_type == MICCAPProviderType.CENTER,
                provider_type == MICCAPProviderType.FAMILY_HOME,
            ],
            [
                center_rate,
                family_home_rate,
            ],
            default=exempt_rate,
        )
