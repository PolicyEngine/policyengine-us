from policyengine_us.model_api import *


class NHSSPLivingArrangement(Enum):
    INDEPENDENT = "Independent living"
    SUBSIDIZED_COMMUNITY_RESIDENCE = "Certified subsidized community residence"
    NONSUBSIDIZED_COMMUNITY_RESIDENCE = "Certified nonsubsidized community residence"
    ENHANCED_FAMILY_CARE = "Certified enhanced family care"
    RESIDENTIAL_CARE = "Certified residential care"
    NONE = "No eligible adult assistance living arrangement"


class nh_ssp_living_arrangement(Variable):
    value_type = Enum
    entity = Person
    label = "New Hampshire adult assistance living arrangement"
    definition_period = MONTH
    possible_values = NHSSPLivingArrangement
    default_value = NHSSPLivingArrangement.INDEPENDENT
    # PDF pages 14-16
    reference = "https://www.medicaid.gov/medicaid/spa/downloads/NH-26-0001.pdf#page=14"
    documentation = """
    Care categories require state approval. Care recipients are individual
    assistance groups, including married residents. Reflect separate federal
    SSI claims explicitly when applicable. Use NONE for excluded facilities.
    """

    def formula(person, period, parameters):
        return where(
            person("ssi_lives_in_medical_treatment_facility", period),
            NHSSPLivingArrangement.NONE,
            NHSSPLivingArrangement.INDEPENDENT,
        )
