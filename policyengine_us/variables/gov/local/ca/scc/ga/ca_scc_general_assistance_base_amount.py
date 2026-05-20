from policyengine_us.model_api import *


class ca_scc_general_assistance_base_amount(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "Santa Clara County General Assistance base amount"
    defined_for = "ca_scc_general_assistance_eligible_person"
    reference = (
        "https://stgenssa.sccgov.org/debs/program_handbooks/charts/assets/4GA/NeedStnds.htm",
        "https://stgenssa.sccgov.org/debs/program_handbooks/general_assistance/assets/14Payment/Shared_Housing.htm",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.scc.general_assistance
        eligible_persons = spm_unit.members(
            "ca_scc_general_assistance_eligible_person", period
        )
        num_eligible = spm_unit.sum(eligible_persons)
        unshared = where(num_eligible == 2, p.amount.married, p.amount.single)
        shared_status = spm_unit(
            "ca_scc_general_assistance_shared_housing_status", period
        )
        reduction = p.shared_housing.reduction[shared_status]
        return unshared * (1 - reduction)
