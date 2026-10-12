from policyengine_us.model_api import *


class CaSMCGeneralAssistanceLivingArrangement(Enum):
    INDEPENDENT_LIVING = "Independent living"
    DRUG_ALCOHOL_TREATMENT_CENTER = "Drug and alcohol treatment center"
    NMOHC_WITHOUT_REFERRAL = "Non-medical out-of-home care without BHRS/SMMC referral"
    NMOHC_WITH_REFERRAL = "Non-medical out-of-home care with BHRS/SMMC referral"


class ca_smc_general_assistance_living_arrangement(Variable):
    value_type = Enum
    entity = SPMUnit
    label = "San Mateo County General Assistance living arrangement"
    definition_period = MONTH
    defined_for = "in_smc"
    possible_values = CaSMCGeneralAssistanceLivingArrangement
    default_value = CaSMCGeneralAssistanceLivingArrangement.INDEPENDENT_LIVING
    reference = "https://www.smcgov.org/media/156974/download?inline=#page=2"
