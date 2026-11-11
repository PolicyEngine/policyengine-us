from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


class ut_dhhs_ssp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Utah DHHS State Supplemental Payment"
    definition_period = MONTH
    defined_for = StateCode.UT
    reference = (
        "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R414-306-6",
        "https://oepmanuals.dhhs.utah.gov/600_Program_Benefits/661_Fifteen_Dollar_State_Supplemental_Payment_%28SSP%29.htm",
    )
    documentation = """
    Set ssi_lives_in_medical_treatment_facility and
    ssi_medicaid_pays_majority_of_care to true while the person lives in a
    medical treatment facility where Medicaid pays more than half the cost of
    care, which limits SSI to the federal facility rate. Utah Medicaid
    enrollment is computed from Medicaid eligibility and take-up. Set
    receives_ssi when the person reports an SSI payment that the model does
    not compute.
    """
    # NOTE: the microdata do not populate ssi_lives_in_medical_treatment_facility
    # or ssi_medicaid_pays_majority_of_care, so this payment reaches household
    # calculations only.

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ut.dhhs.ssp
        # NOTE: R414-306-6(2) requires that the resident "receives a
        # Supplemental Security Income (SSI) payment"; Manual 661 sets the
        # floor ("The SSI payment must be at least $1.00"), which the model
        # applies through minimum_ssi_payment.
        receives_ssi = (person("ssi", period) >= p.minimum_ssi_payment) | person(
            "receives_ssi", period
        )
        arrangement = person("ssi_federal_living_arrangement", period)
        medical = arrangement == SSIFederalLivingArrangement.MEDICAL_TREATMENT_FACILITY
        medicaid = person(
            "medicaid_enrolled_for_ssi_state_supplement", period.this_year
        )
        return receives_ssi & medical & medicaid
