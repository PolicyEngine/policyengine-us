from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


class PASSPLivingArrangement(Enum):
    INDEPENDENT = "Independent living"
    HOUSEHOLD_OF_ANOTHER = "Household of another"
    DOMICILIARY_CARE = "State-certified domiciliary care home"
    PERSONAL_CARE = "Licensed personal care home, certified for the supplement"
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
    Certified domiciliary and personal care home residence comes from
    pa_ssp_care_home and does not change federal SSI claim or income
    calculations. SSA applies the personal care home couple rate only in the
    month of the move; from the next month both spouses are individual
    recipients (POMS SI 01415.058 K.2.b NOTE). For those periods override
    ssi_claim_is_joint (a yearly formula variable) to false for both spouses,
    which also sets each spouse's federal SSI amount; an input replaces the
    formula for everyone in the simulation, so set it to true for any other
    joint couple. Certified care home residents are in federal living
    arrangement A (POMS SI PHI01415.010 G.3), so do not also set the
    household-of-another SSI inputs for them.
    Domiciliary care couples keep the couple rate, and in the move month
    Pennsylvania pays each spouse of a mixed-arrangement couple half of their
    own couple rate (POMS SI PHI01415.010 Appendix I Chart 35 note 2). The
    shared state supplement helper instead gives each spouse in a joint
    mixed-arrangement couple the average of the two couple rates, with the same
    couple total unless income reduces one spouse's half to zero.
    """

    def formula(person, period, parameters):
        federal = person("ssi_federal_living_arrangement", period)
        care_home = person("pa_ssp_care_home", period)
        care_homes = care_home.possible_values
        # Title XIX facility residents first (55 Pa. Code § 299.21(b)(3)); care
        # homes are non-medical (POMS SI 01415.058 K.1) and in arrangement A
        # (POMS SI PHI01415.010 G.3), so they precede the household of another.
        return select(
            [
                federal == SSIFederalLivingArrangement.MEDICAL_TREATMENT_FACILITY,
                care_home == care_homes.DOMICILIARY_CARE,
                care_home == care_homes.PERSONAL_CARE,
                federal == SSIFederalLivingArrangement.ANOTHER_PERSONS_HOUSEHOLD,
            ],
            [
                PASSPLivingArrangement.MEDICAID_INSTITUTION,
                PASSPLivingArrangement.DOMICILIARY_CARE,
                PASSPLivingArrangement.PERSONAL_CARE,
                PASSPLivingArrangement.HOUSEHOLD_OF_ANOTHER,
            ],
            default=PASSPLivingArrangement.INDEPENDENT,
        )
