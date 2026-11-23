from policyengine_us.model_api import *


class ILLIHEAPNaturalGasProvider(Enum):
    # The natural gas distribution company named on the bill. Customers of
    # the four listed companies use the state-funded income limit and the
    # low-income discount payment matrix. A household with heat included in
    # rent (the cash route) keeps the federal income limit, because the
    # PY2027 chart prints no cash row above 60% SMI.
    AMEREN_ILLINOIS = "Ameren Illinois"
    NICOR_GAS = "Nicor Gas"
    NORTH_SHORE_GAS = "North Shore Gas"
    PEOPLES_GAS = "Peoples Gas"
    # A reported company outside the listed choices.
    OTHER = "Other natural gas provider"
    # The company was not reported. It counts as a state-funded company for
    # the income limit, with the same cash-route exception, and uses the
    # general payment matrix.
    UNSPECIFIED = "Unspecified"


class il_liheap_natural_gas_provider(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = ILLIHEAPNaturalGasProvider
    default_value = ILLIHEAPNaturalGasProvider.UNSPECIFIED
    definition_period = YEAR
    label = "Illinois LIHEAP natural gas provider"
    defined_for = StateCode.IL
    reference = (
        "https://dceo.illinois.gov/communityservices/utilitybillassistance/howtoapply.html",
        "https://www.ilga.gov/documents/legislation/ilcs/documents/030500200K6.htm",
        "https://www.icc.illinois.gov/consumers/utility-energy-assistance",
    )
