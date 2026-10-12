from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


class NYSSPLivingArrangement(Enum):
    LIVING_ALONE = "Living alone"
    LIVING_WITH_OTHERS = "Living with others"
    FAMILY_CARE = "Certified congregate care level I"
    RESIDENTIAL_CARE = "Certified congregate care level II"
    ENHANCED_RESIDENTIAL_CARE = "Certified congregate care level III"
    NURSING_FACILITY = "Department of Health licensed nursing facility"
    OTHER_MEDICAL_FACILITY = "Other qualifying Medicaid medical facility"
    NONE = "No eligible New York living arrangement"


class ny_ssp_living_arrangement(Variable):
    value_type = Enum
    entity = Person
    label = "New York State Supplement Program living arrangement"
    definition_period = MONTH
    defined_for = StateCode.NY
    possible_values = NYSSPLivingArrangement
    default_value = NYSSPLivingArrangement.NONE
    reference = "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-398-4.5"
    documentation = """
    Set certified care categories explicitly. Family and residential care for
    minors require the authorized placements specified in 18 NYCRR 398-4.5.
    The formula uses household membership; set LIVING_ALONE explicitly for
    qualifying separate-food, room-and-board, foster-child or attendant cases.
    Use NONE for excluded public facilities and emergency shelters. Nursing
    facilities must be identified explicitly; other Medicaid institutions use
    the lower medical-facility allowance. Set SSI claim status explicitly for
    institutional couples after their month of entry.
    """

    def formula(person, period, parameters):
        la = NYSSPLivingArrangement
        federal = person("ssi_federal_living_arrangement", period)
        medical = federal == SSIFederalLivingArrangement.MEDICAL_TREATMENT_FACILITY
        excluded = person("ssi_lives_in_medical_treatment_facility", period) & ~medical
        other = federal == SSIFederalLivingArrangement.ANOTHER_PERSONS_HOUSEHOLD
        joint = person("ssi_couple_computation_applies", period)
        alone = person.household.nb_persons() == where(joint, 2, 1)
        minor = person("ny_ssp_is_minor", period.this_year)
        return select(
            [excluded, medical, other | minor | ~alone],
            [la.NONE, la.OTHER_MEDICAL_FACILITY, la.LIVING_WITH_OTHERS],
            default=la.LIVING_ALONE,
        )
