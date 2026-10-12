from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


class RISSPLivingArrangement(Enum):
    INDEPENDENT = "Own household"
    HOUSEHOLD_OF_ANOTHER = "Household of another"
    RESIDENTIAL_CARE = "State-certified residential care or assisted living"
    MEDICAID_INSTITUTION = "Title XIX facility"
    NONE = "No supplement"


class ri_ssp_living_arrangement(Variable):
    value_type = Enum
    entity = Person
    label = "Rhode Island SSP living arrangement"
    definition_period = MONTH
    defined_for = StateCode.RI
    possible_values = RISSPLivingArrangement
    default_value = RISSPLivingArrangement.NONE
    reference = "https://rules.sos.ri.gov/regulations/Part/218-20-00-5"
    documentation = """
    Certified care is an explicit input. Enter separate individual SSI claims
    when institutional residence ends eligible-couple status; the care input
    itself does not override federal SSI claim or income calculations.
    """

    def formula(person, period, parameters):
        federal = person("ssi_federal_living_arrangement", period)
        return select(
            [
                federal == SSIFederalLivingArrangement.MEDICAL_TREATMENT_FACILITY,
                federal == SSIFederalLivingArrangement.ANOTHER_PERSONS_HOUSEHOLD,
            ],
            [
                RISSPLivingArrangement.MEDICAID_INSTITUTION,
                RISSPLivingArrangement.HOUSEHOLD_OF_ANOTHER,
            ],
            default=RISSPLivingArrangement.INDEPENDENT,
        )
