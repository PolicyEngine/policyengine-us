from policyengine_us.model_api import *


class WAWCCCProviderType(Enum):
    FAMILY_HOME = "Licensed Family Home"
    IN_HOME_RELATIVE = "License-Exempt In-Home/Relative"
    CENTER = "Licensed Center"


class wa_wccc_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = WAWCCCProviderType
    default_value = WAWCCCProviderType.CENTER
    definition_period = MONTH
    label = "Washington WCCC child care provider type"
    defined_for = "wa_wccc_eligible_child"
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0200",
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0205",
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0240",
    )
