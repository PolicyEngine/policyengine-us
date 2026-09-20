from policyengine_us.model_api import *


class id_iccp_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Eligible for the Idaho Child Care Program"
    defined_for = StateCode.ID
    reference = "https://adminrules.idaho.gov/rules/current/16/160612.pdf#page=12"

    def formula(spm_unit, period, parameters):
        # Intentional limitations: we don't track these ICCP pathways at the
        # moment - court-ordered disability child eligibility (IDAPA
        # 16.06.12.105.03.b), the incapacitated-parent activity exemption
        # (106), the 3-month continuation after a qualifying activity ceases
        # (202), the child immunization requirement (105.01), and the
        # graduated phase-out for income between 175% FPG and the State Plan
        # limit at redetermination (070.03 / 602.02).
        has_eligible_child = add(spm_unit, period, ["id_iccp_eligible_child"]) > 0
        return (
            has_eligible_child
            & spm_unit("id_iccp_income_eligible", period)
            & spm_unit("is_ccdf_asset_eligible", period.this_year)
            & spm_unit("id_iccp_activity_eligible", period)
        )
