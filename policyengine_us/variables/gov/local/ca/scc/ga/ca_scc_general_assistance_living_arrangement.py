from policyengine_us.model_api import *


class CaSccGeneralAssistanceLivingArrangement(Enum):
    NOT_SHARED = "Not shared"
    SHARED_WITH_ONE = "Shared with one other person"
    SHARED_WITH_TWO = "Shared with two other persons"
    SHARED_WITH_THREE_OR_MORE = "Shared with three or more other persons"
    BOARD_AND_CARE = "State-licensed Board and Care or Residential Care Home"
    MEDICAL_INSTITUTION = "Medical institution"


class ca_scc_general_assistance_living_arrangement(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = CaSccGeneralAssistanceLivingArrangement
    default_value = CaSccGeneralAssistanceLivingArrangement.NOT_SHARED
    definition_period = MONTH
    label = "Santa Clara County General Assistance living arrangement"
    reference = (
        "https://stgenssa.sccgov.org/debs/program_handbooks/charts/assets/4GA/NeedStnds.htm",
        "https://stgenssa.sccgov.org/debs/Forms/GA_62_en.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        federal_arrangement = spm_unit.members("ssi_federal_living_arrangement", period)
        in_medical = (
            federal_arrangement
            == federal_arrangement.possible_values.MEDICAL_TREATMENT_FACILITY
        )
        any_in_medical = spm_unit.any(in_medical)
        any_in_rcf = add(spm_unit, period, ["is_in_residential_care_facility"]) > 0

        return select(
            [any_in_medical, any_in_rcf],
            [
                CaSccGeneralAssistanceLivingArrangement.MEDICAL_INSTITUTION,
                CaSccGeneralAssistanceLivingArrangement.BOARD_AND_CARE,
            ],
            default=CaSccGeneralAssistanceLivingArrangement.NOT_SHARED,
        )
