from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)
from policyengine_us.variables.gov.states.ny.otda.ssp.ny_ssp_care_setting import (
    NYSSPCareSetting,
)


class NYSSPLivingArrangement(Enum):
    LIVING_ALONE = "Living alone"
    LIVING_WITH_OTHERS = "Living with others"
    FAMILY_CARE = "Certified congregate care level I"
    RESIDENTIAL_CARE = "Certified congregate care level II"
    ENHANCED_RESIDENTIAL_CARE = "Certified congregate care level III"
    RESIDENTIAL_HEALTH_CARE_FACILITY = "Residential health care facility"
    DEVELOPMENTAL_OR_MENTAL_HEALTH_FACILITY = (
        "OPWDD intermediate care facility or OMH hospital"
    )
    NONE = "No eligible New York living arrangement"


class ny_ssp_living_arrangement(Variable):
    value_type = Enum
    entity = Person
    label = "New York State Supplement Program living arrangement"
    definition_period = MONTH
    defined_for = StateCode.NY
    possible_values = NYSSPLivingArrangement
    default_value = NYSSPLivingArrangement.NONE
    reference = (
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-398-4.5",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-398-3.4",
    )
    documentation = """
    Care levels and designated facilities come from ny_ssp_care_setting.
    Residents of medical facilities where Medicaid pays more than half the
    cost default to a residential health care facility (nursing home). Set
    this variable for every member of the household only for the separate-food,
    room-and-board, homemaker, family care resident or aide cases that
    18 NYCRR 398-4.5(a)(1) counts as living alone.
    """

    def formula(person, period, parameters):
        la = NYSSPLivingArrangement
        care = person("ny_ssp_care_setting", period)
        federal = person("ssi_federal_living_arrangement", period)
        medical = federal == SSIFederalLivingArrangement.MEDICAL_TREATMENT_FACILITY
        in_facility = person("ssi_lives_in_medical_treatment_facility", period)
        designated = care == NYSSPCareSetting.DEVELOPMENTAL_OR_MENTAL_HEALTH_FACILITY
        excluded = (care == NYSSPCareSetting.EXCLUDED) | (
            (in_facility | designated) & ~medical
        )
        other = federal == SSIFederalLivingArrangement.ANOTHER_PERSONS_HOUSEHOLD
        joint = person("ssi_couple_computation_applies", period)
        # 18 NYCRR 398-4.5(a) defines living alone by the private household.
        # Foster children do not end it ((a)(1)(vi), (a)(2)(ii)), and a member
        # living in a medical facility is not part of the household.
        household_member = ~person("is_in_foster_care", period) & ~in_facility
        alone = person.household.sum(household_member) == where(
            joint, person.marital_unit.sum(household_member), 1
        )
        minor = person("ny_ssp_is_minor", period.this_year)
        return select(
            [
                excluded,
                medical & designated,
                medical,
                care == NYSSPCareSetting.FAMILY_CARE,
                care == NYSSPCareSetting.RESIDENTIAL_CARE,
                care == NYSSPCareSetting.ENHANCED_RESIDENTIAL_CARE,
                other | minor | ~alone,
            ],
            [
                la.NONE,
                la.DEVELOPMENTAL_OR_MENTAL_HEALTH_FACILITY,
                la.RESIDENTIAL_HEALTH_CARE_FACILITY,
                la.FAMILY_CARE,
                la.RESIDENTIAL_CARE,
                la.ENHANCED_RESIDENTIAL_CARE,
                la.LIVING_WITH_OTHERS,
            ],
            default=la.LIVING_ALONE,
        )
