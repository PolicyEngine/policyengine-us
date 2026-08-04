from policyengine_us.model_api import *
from policyengine_us.variables.gov.local.ca.scc.ga.ca_scc_general_assistance_living_arrangement import (
    CaSccGeneralAssistanceLivingArrangement,
)


class ca_scc_general_assistance_base_amount(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "Santa Clara County General Assistance base amount"
    defined_for = "ca_scc_general_assistance_eligible_person"
    reference = (
        "https://stgenssa.sccgov.org/debs/program_handbooks/charts/assets/4GA/NeedStnds.htm",
        "https://stgenssa.sccgov.org/debs/Forms/GA_62_en.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.scc.general_assistance
        eligible_persons = spm_unit.members(
            "ca_scc_general_assistance_eligible_person", period
        )
        num_eligible = spm_unit.sum(eligible_persons)
        unshared = where(num_eligible >= 2, p.amount.married, p.amount.single)
        arrangement = spm_unit("ca_scc_general_assistance_living_arrangement", period)
        reduction = p.shared_housing.reduction[arrangement]
        standard = unshared * (1 - reduction)
        return select(
            [
                arrangement == CaSccGeneralAssistanceLivingArrangement.BOARD_AND_CARE,
                arrangement
                == CaSccGeneralAssistanceLivingArrangement.MEDICAL_INSTITUTION,
            ],
            [
                p.amount.board_and_care,
                p.amount.medical_institution,
            ],
            default=standard,
        )
