from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


class VTAABDLivingArrangement(Enum):
    INDEPENDENT = "Independent living"
    HOUSEHOLD_OF_ANOTHER = "Living in another household"
    RESIDENTIAL_CARE_LEVEL_III = (
        "Level III residential care with assistive community care (PNMI, code C)"
    )
    RESIDENTIAL_CARE_LEVEL_IV = (
        "State-identified Level IV residential or therapeutic care"
    )
    CUSTODIAL_CARE = "Qualifying custodial family home"
    MEDICAID_INSTITUTION = "Title XIX medical institution"
    NONE = "Supplement waived or no qualifying arrangement"


class vt_aabd_living_arrangement(Variable):
    value_type = Enum
    entity = Person
    label = "Vermont AABD living arrangement"
    definition_period = MONTH
    defined_for = StateCode.VT
    possible_values = VTAABDLivingArrangement
    default_value = VTAABDLivingArrangement.NONE
    reference = (
        "https://secure.ssa.gov/poms.nsf/lnx/0501415058#m",
        "https://secure.ssa.gov/poms.nsf/lnx/0501415970BOS",
        "https://secure.ssa.gov/poms.nsf/lnx/0501415013BOS",
        # PDF pages 28, 31
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2700-AABD.pdf#page=28",
    )
    documentation = """
    Defaults follow federal SSI living arrangements. Residential and custodial
    care require an explicit setting that meets the state's certification and
    service rules. Independent rates are identical inside and outside Chittenden
    County in 2026. Children under 18 in a facility paid by private health
    insurance map to independent living (SI BOS01415.970). The state-administered
    Level III residential care home with limited nursing care (rule 2764.2) is
    not modeled; SI BOS01415.013 reports that all such homes converted to code C.
    """

    def formula(person, period, parameters):
        federal = person("ssi_federal_living_arrangement", period)
        return select(
            [
                federal == SSIFederalLivingArrangement.MEDICAL_TREATMENT_FACILITY,
                federal == SSIFederalLivingArrangement.ANOTHER_PERSONS_HOUSEHOLD,
            ],
            [
                VTAABDLivingArrangement.MEDICAID_INSTITUTION,
                VTAABDLivingArrangement.HOUSEHOLD_OF_ANOTHER,
            ],
            default=VTAABDLivingArrangement.INDEPENDENT,
        )
