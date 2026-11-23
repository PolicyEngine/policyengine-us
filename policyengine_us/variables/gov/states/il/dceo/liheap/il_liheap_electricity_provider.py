from policyengine_us.model_api import *


class ILLIHEAPElectricityProvider(Enum):
    # The electric distribution company named on the bill. Ameren Illinois
    # and ComEd customers use the state-funded income limit, and ComEd
    # customers use the ComEd payment matrices. A household with heat
    # included in rent (the cash route) keeps the federal income limit,
    # because the PY2027 chart prints no cash row above 60% SMI.
    AMEREN_ILLINOIS = "Ameren Illinois"
    COMED = "ComEd"
    # A reported company outside the listed choices.
    OTHER = "Other electricity provider"
    # The company was not reported. It counts as a state-funded company for
    # the income limit, with the same cash-route exception, and uses the
    # general payment matrix.
    UNSPECIFIED = "Unspecified"


class il_liheap_electricity_provider(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = ILLIHEAPElectricityProvider
    default_value = ILLIHEAPElectricityProvider.UNSPECIFIED
    definition_period = YEAR
    label = "Illinois LIHEAP electricity provider"
    defined_for = StateCode.IL
    reference = (
        "https://dceo.illinois.gov/communityservices/utilitybillassistance/howtoapply.html",
        "https://www.ilga.gov/documents/legislation/ilcs/documents/030500200K6.htm",
        "https://www.icc.illinois.gov/consumers/utility-energy-assistance",
    )
