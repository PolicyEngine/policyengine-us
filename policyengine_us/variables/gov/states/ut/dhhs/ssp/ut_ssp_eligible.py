from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


class ut_ssp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Utah State Supplemental Payment"
    definition_period = MONTH
    defined_for = StateCode.UT
    reference = "https://oepmanuals.dhhs.utah.gov/600_Program_Benefits/661_Fifteen_Dollar_State_Supplemental_Payment_%28SSP%29.htm"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ut.dhhs.ssp
        federal = parameters(period).gov.ssa.ssi.amount
        ssi = person("ssi", period)
        arrangement = person("ssi_federal_living_arrangement", period)
        medical = arrangement == SSIFederalLivingArrangement.MEDICAL_TREATMENT_FACILITY
        medicaid = person(
            "medicaid_enrolled_for_ssi_state_supplement", period.this_year
        )
        return (
            medical
            & medicaid
            & (ssi >= p.minimum_ssi_payment)
            & (ssi <= federal.medical_facility)
        )
