from policyengine_us.model_api import *


class MNEAPHousingType(Enum):
    APARTMENT = "Apartment"
    DUPLEX = "Duplex"
    TRIPLEX = "Triplex"
    FOURPLEX = "Fourplex"
    TOWNHOUSE = "Townhouse"
    HOUSE = "House"
    MOBILE_HOME = "Mobile home"
    OTHER = "Other"


class mn_eap_housing_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = MNEAPHousingType
    default_value = MNEAPHousingType.HOUSE
    definition_period = YEAR
    label = "Minnesota EAP housing type"
    documentation = (
        "Housing type column of the Minnesota EAP backup matrix, used for "
        "households with heat included in rent. If omitted, the model assumes "
        "a house; report the type to apply the matching average energy cost."
    )
    defined_for = StateCode.MN
    reference = (
        # PDF pages 125-126
        "https://mn.gov/commerce-stat/pdfs/ffy26-eap-policy-manual.pdf#page=125",
        # PDF pages 127-128
        "https://mn.gov/commerce-stat/pdfs/ffy27-eap-policy-manual.pdf#page=127",
        "https://mn.gov/commerce-stat/xls/phb-calculator.xlsx",
    )
