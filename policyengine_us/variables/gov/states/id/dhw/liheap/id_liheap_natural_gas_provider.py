from policyengine_us.model_api import *


class IDLIHEAPNaturalGasProvider(Enum):
    # The natural gas company named on the bill. It selects the Intermountain
    # Gas or Avista column of the heating matrix and the estimated heating
    # costs.
    INTERMOUNTAIN_GAS = "Intermountain Gas"
    AVISTA = "Avista"
    # A reported company outside the listed choices, or a company that was
    # not reported. Both use the Intermountain Gas column.
    OTHER = "Other natural gas provider"
    UNSPECIFIED = "Unspecified"


class id_liheap_natural_gas_provider(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = IDLIHEAPNaturalGasProvider
    default_value = IDLIHEAPNaturalGasProvider.UNSPECIFIED
    definition_period = YEAR
    label = "Idaho LIHEAP natural gas provider"
    defined_for = StateCode.ID
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/ID_BenefitMatrix_Heating_2026.pdf#page=1",
        "https://web.archive.org/web/20170127123014id_/http://www.healthandwelfare.idaho.gov/Portals/_Rainbow/Manuals/LIHEAP/Appendices/c_htgcost_matrix_PY07.pdf#page=1",
    )
