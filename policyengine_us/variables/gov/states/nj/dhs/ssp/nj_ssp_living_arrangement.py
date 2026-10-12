from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.nj.dhs.ssp.nj_ssp_care_setting import (
    NJSSPCareSetting,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


class NJSSPLivingArrangement(Enum):
    LIVING_ALONE_OR_WITH_OTHERS = "Living alone or with others"
    LIVING_ONLY_WITH_INELIGIBLE_SPOUSE = "Living only with an ineligible spouse"
    CONGREGATE_CARE = "Certified congregate care"
    RESIDENTIAL_HEALTH_CARE = "Certified residential health care"
    HOUSEHOLD_OF_ANOTHER = "Household of another"
    MEDICAID_INSTITUTION = "Medicaid institution"
    NONE = "No supplement"


class nj_ssp_living_arrangement(Variable):
    value_type = Enum
    entity = Person
    label = "New Jersey SSP living arrangement"
    definition_period = MONTH
    defined_for = StateCode.NJ
    possible_values = NJSSPLivingArrangement
    default_value = NJSSPLivingArrangement.NONE
    reference = "https://secure.ssa.gov/poms.nsf/lnx/0501415025NY"
    documentation = """
    A separately purchasing couple sharing an address with others, or a couple
    living only with foster children, can set the ineligible-spouse variation
    explicitly after the state's household determination.
    """

    def formula(person, period, parameters):
        care = person("nj_ssp_care_setting", period)
        federal = person("ssi_federal_living_arrangement", period)
        medical = federal == SSIFederalLivingArrangement.MEDICAL_TREATMENT_FACILITY
        other_medical = (
            person("ssi_lives_in_medical_treatment_facility", period) & ~medical
        )
        ineligible_spouse = person.marital_unit.any(
            person("is_ssi_ineligible_spouse", period.this_year)
        )
        no_others = person.household.nb_persons() == person.marital_unit.nb_persons()
        return select(
            [
                (care == NJSSPCareSetting.EXCLUDED) | other_medical,
                medical,
                care == NJSSPCareSetting.CONGREGATE_CARE,
                care == NJSSPCareSetting.RESIDENTIAL_HEALTH_CARE,
                federal == SSIFederalLivingArrangement.ANOTHER_PERSONS_HOUSEHOLD,
                ineligible_spouse & no_others,
            ],
            [
                NJSSPLivingArrangement.NONE,
                NJSSPLivingArrangement.MEDICAID_INSTITUTION,
                NJSSPLivingArrangement.CONGREGATE_CARE,
                NJSSPLivingArrangement.RESIDENTIAL_HEALTH_CARE,
                NJSSPLivingArrangement.HOUSEHOLD_OF_ANOTHER,
                NJSSPLivingArrangement.LIVING_ONLY_WITH_INELIGIBLE_SPOUSE,
            ],
            default=NJSSPLivingArrangement.LIVING_ALONE_OR_WITH_OTHERS,
        )
