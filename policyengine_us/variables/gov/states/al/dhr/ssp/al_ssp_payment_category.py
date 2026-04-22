from policyengine_us.model_api import *


class ALSSPPaymentCategory(Enum):
    FCMP_NURSING_CARE = "FCMP Nursing Care"
    NURSING_CARE = "Nursing Care Supplement"
    IHC_LEVEL_A = "Independent Homelife Care, Level A"
    IHC_LEVEL_B = "Independent Homelife Care, Level B"
    FOSTER_CARE = "Foster Home Care"
    CEREBRAL_PALSY = "Cerebral Palsy Treatment Center"
    NONE = "Not in a qualifying care arrangement"


class al_ssp_payment_category(Variable):
    value_type = Enum
    entity = Person
    label = "Alabama SSP payment category"
    definition_period = MONTH
    defined_for = StateCode.AL
    possible_values = ALSSPPaymentCategory
    default_value = ALSSPPaymentCategory.NONE
    reference = (
        "https://admincode.legislature.state.al.us/api/chapter/660-2-4#page=9",
        "https://admincode.legislature.state.al.us/api/chapter/660-2-4#page=10",
        "https://admincode.legislature.state.al.us/api/chapter/660-2-4#page=14",
    )

    def formula(person, period):
        legacy_arrangement = person("al_ssp_living_arrangement", period)
        legacy = legacy_arrangement.possible_values
        care_setting = person("al_ssp_care_setting", period)
        care = care_setting.possible_values

        is_nursing = care_setting == care.NURSING_FACILITY
        medicaid_pays = person("ssi_medicaid_pays_majority_of_care", period.this_year)

        is_ihc = care_setting == care.PRIVATE_HOME_IHC
        level_b = person("al_level_b_care", period)

        # Legacy al_ssp_living_arrangement branches are listed first
        # so that consumers still providing that input take priority
        # over the newer al_ssp_care_setting derivation. This preserves
        # backward compatibility; reordering would break existing API
        # consumers.
        return select(
            [
                legacy_arrangement == legacy.FCMP_NURSING_CARE,
                legacy_arrangement == legacy.NURSING_CARE,
                legacy_arrangement == legacy.IHC_LEVEL_A,
                legacy_arrangement == legacy.IHC_LEVEL_B,
                legacy_arrangement == legacy.FOSTER_CARE,
                legacy_arrangement == legacy.CEREBRAL_PALSY,
                is_nursing & medicaid_pays,
                is_nursing & ~medicaid_pays,
                is_ihc & level_b,
                is_ihc & ~level_b,
                care_setting == care.FOSTER_HOME,
                care_setting == care.CEREBRAL_PALSY_CENTER,
            ],
            [
                ALSSPPaymentCategory.FCMP_NURSING_CARE,
                ALSSPPaymentCategory.NURSING_CARE,
                ALSSPPaymentCategory.IHC_LEVEL_A,
                ALSSPPaymentCategory.IHC_LEVEL_B,
                ALSSPPaymentCategory.FOSTER_CARE,
                ALSSPPaymentCategory.CEREBRAL_PALSY,
                ALSSPPaymentCategory.FCMP_NURSING_CARE,
                ALSSPPaymentCategory.NURSING_CARE,
                ALSSPPaymentCategory.IHC_LEVEL_B,
                ALSSPPaymentCategory.IHC_LEVEL_A,
                ALSSPPaymentCategory.FOSTER_CARE,
                ALSSPPaymentCategory.CEREBRAL_PALSY,
            ],
            default=ALSSPPaymentCategory.NONE,
        )
