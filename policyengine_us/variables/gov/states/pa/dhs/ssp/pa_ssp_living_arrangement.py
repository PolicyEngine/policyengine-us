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
    reference = (
        "https://www.pacodeandbulletin.gov/secure/pacode/data/055/chapter299/s299.1.html",
        "https://secure.ssa.gov/poms.nsf/lnx/0501415058#k",
    )
    documentation = """
    Certified domiciliary and personal care home residence is an explicit input
    and does not change federal SSI claim or income calculations. SSA applies
    the personal care home couple rate only in the month of the move; from the
    next month both spouses are individual recipients (POMS SI 01415.058 K.2.b
    NOTE). For those months enter the spouses as separate individual SSI claims
    (ssi_claim_is_joint false), which also sets each spouse's federal SSI
    amount. Domiciliary care couples keep the couple rate, and in the move month
    Pennsylvania pays each spouse of a mixed-arrangement couple half of their
    own couple rate (POMS SI PHI01415.010 Appendix I Chart 35 note 2). The
    shared state supplement helper instead gives each spouse in a joint
    mixed-arrangement couple the average of the two couple rates, with the same
    couple total.
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
