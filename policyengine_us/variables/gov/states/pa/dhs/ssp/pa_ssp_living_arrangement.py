from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


class PASSPLivingArrangement(Enum):
    INDEPENDENT = "Independent living"
    HOUSEHOLD_OF_ANOTHER = "Household of another"
    DOMICILIARY_CARE = "State-certified domiciliary care home"
    PERSONAL_CARE = "State-certified personal care home"
    MEDICAID_INSTITUTION = "Medicaid long-term care institution"
    NONE = "No supplement"


class pa_ssp_living_arrangement(Variable):
    value_type = Enum
    entity = Person
    label = "Pennsylvania SSP living arrangement"
    definition_period = MONTH
    defined_for = StateCode.PA
    possible_values = PASSPLivingArrangement
    default_value = PASSPLivingArrangement.NONE
    reference = "https://www.pacodeandbulletin.gov/secure/pacode/data/055/chapter299/chap299toc.html"
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
                PASSPLivingArrangement.MEDICAID_INSTITUTION,
                PASSPLivingArrangement.HOUSEHOLD_OF_ANOTHER,
            ],
            default=PASSPLivingArrangement.INDEPENDENT,
        )
