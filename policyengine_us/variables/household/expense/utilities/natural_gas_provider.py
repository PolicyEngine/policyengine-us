from policyengine_us.model_api import *


class NaturalGasProvider(Enum):
    UNSPECIFIED = "Unspecified"
    AMEREN_ILLINOIS = "Ameren Illinois"
    AVISTA = "Avista"
    INTERMOUNTAIN_GAS = "Intermountain Gas"
    NICOR_GAS = "Nicor Gas"
    NORTH_SHORE_GAS = "North Shore Gas"
    PEOPLES_GAS = "Peoples Gas"
    RHODE_ISLAND_ENERGY = "Rhode Island Energy (Narragansett Electric)"
    OTHER = "Other natural gas provider"


class natural_gas_provider(Variable):
    value_type = Enum
    possible_values = NaturalGasProvider
    default_value = NaturalGasProvider.UNSPECIFIED
    entity = SPMUnit
    definition_period = YEAR
    label = "Natural gas utility provider"
    documentation = (
        "Company providing the home's natural gas distribution service, as named "
        "on the utility bill. Report the distribution utility even when a "
        "separate retailer supplies the gas. UNSPECIFIED means the company was "
        "not reported; OTHER means a reported company outside the listed choices. "
        "The choices initially cover named utilities needed for Idaho, Illinois "
        "and Rhode Island heating assistance and can be extended for other "
        "programs. Electricity and gas companies are reported independently. "
        "This input does not imply program enrollment or bill receipt."
    )
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/ID_BenefitMatrix_Heating_2026.pdf#page=1",
        "https://dceo.illinois.gov/communityservices/utilitybillassistance/howtoapply.html",
        "https://webserver.rilegislature.gov/Statutes/TITLE39/39-1/39-1-27.12.htm",
    )
