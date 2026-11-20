from policyengine_us.model_api import *


class IDLIHEAPNaturalGasProvider(Enum):
    INTERMOUNTAIN_GAS = "Intermountain Gas"
    AVISTA = "Avista"
    OTHER = "Other natural gas provider"
    UNSPECIFIED = "Unspecified"


class id_liheap_natural_gas_provider(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = IDLIHEAPNaturalGasProvider
    default_value = IDLIHEAPNaturalGasProvider.UNSPECIFIED
    definition_period = YEAR
    label = "Idaho LIHEAP natural gas provider"
    documentation = (
        "Company providing the home's natural gas service, as named on the "
        "gas bill. It selects the Intermountain Gas or Avista column of the "
        "Idaho LIHEAP heating matrix and estimated heating costs. OTHER means "
        "a reported company outside the listed choices and UNSPECIFIED (the "
        "default) means the company was not reported; both use the "
        "Intermountain Gas column."
    )
    defined_for = StateCode.ID
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/ID_BenefitMatrix_Heating_2026.pdf#page=1",
        "https://web.archive.org/web/20170127123014id_/http://www.healthandwelfare.idaho.gov/Portals/_Rainbow/Manuals/LIHEAP/Appendices/c_htgcost_matrix_PY07.pdf#page=1",
    )
