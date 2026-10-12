from policyengine_us.model_api import *


class WISharesProviderType(Enum):
    LICENSED_GROUP = "Licensed group"
    LICENSED_FAMILY = "Licensed family"
    CERTIFIED = "Certified"


class wi_shares_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = WISharesProviderType
    default_value = WISharesProviderType.LICENSED_GROUP
    definition_period = MONTH
    label = "Wisconsin Shares child care provider type"
    defined_for = StateCode.WI
    reference = (
        "https://dcf.wisconsin.gov/wisconsin-shares/wisconsin-shares-handbook-july-2026#page=156",
        "https://dcf.wisconsin.gov/files/wishares/pdf/max-rates-statewide.pdf#page=26",
    )
    # The maximum rate tables merge regularly and provisionally certified
    # providers into a single Certified category (Section 18.5.1).
