from policyengine_us.model_api import *


class ILLIHEAPElectricityProvider(Enum):
    AMEREN_ILLINOIS = "Ameren Illinois"
    COMED = "ComEd"
    OTHER = "Other electricity provider"
    UNSPECIFIED = "Unspecified"


class il_liheap_electricity_provider(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = ILLIHEAPElectricityProvider
    default_value = ILLIHEAPElectricityProvider.UNSPECIFIED
    definition_period = YEAR
    label = "Illinois LIHEAP electricity provider"
    documentation = (
        "Company providing the home's electric distribution service, as named "
        "on the electric bill. Ameren Illinois and ComEd customers use the "
        "state-funded income limit, and ComEd customers use the ComEd payment "
        "matrices. OTHER means a reported company outside the listed choices "
        "and UNSPECIFIED (the default) means the company was not reported; "
        "both use the federally funded income limit and the general payment "
        "matrix."
    )
    defined_for = StateCode.IL
    reference = (
        "https://dceo.illinois.gov/communityservices/utilitybillassistance/howtoapply.html",
        "https://www.ilga.gov/documents/legislation/ilcs/documents/030500200K6.htm",
        "https://www.icc.illinois.gov/consumers/utility-energy-assistance",
    )
