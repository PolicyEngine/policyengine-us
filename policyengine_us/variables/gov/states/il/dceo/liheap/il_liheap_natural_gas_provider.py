from policyengine_us.model_api import *


class ILLIHEAPNaturalGasProvider(Enum):
    AMEREN_ILLINOIS = "Ameren Illinois"
    NICOR_GAS = "Nicor Gas"
    NORTH_SHORE_GAS = "North Shore Gas"
    PEOPLES_GAS = "Peoples Gas"
    OTHER = "Other natural gas provider"
    UNSPECIFIED = "Unspecified"


class il_liheap_natural_gas_provider(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = ILLIHEAPNaturalGasProvider
    default_value = ILLIHEAPNaturalGasProvider.UNSPECIFIED
    definition_period = YEAR
    label = "Illinois LIHEAP natural gas provider"
    documentation = (
        "Company providing the home's natural gas distribution service, as "
        "named on the gas bill. Ameren Illinois, Nicor Gas, North Shore Gas "
        "and Peoples Gas customers use the state-funded income limit and the "
        "low-income discount payment matrix. OTHER means a reported company "
        "outside the listed choices and UNSPECIFIED (the default) means the "
        "company was not reported; both use the federally funded income limit "
        "and the general payment matrix."
    )
    defined_for = StateCode.IL
    reference = (
        "https://dceo.illinois.gov/communityservices/utilitybillassistance/howtoapply.html",
        "https://www.ilga.gov/documents/legislation/ilcs/documents/030500200K6.htm",
        "https://www.icc.illinois.gov/consumers/utility-energy-assistance",
    )
