from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg
from policyengine_us.variables.gov.states.co.ccap.co_ccap_parameter_instant import (
    co_ccap_parameter_instant,
)


class co_ccap_fpg(Variable):
    value_type = float
    entity = SPMUnit
    label = "Colorado Child Care Assistance Program monthly federal poverty guideline"
    unit = USD
    documentation = (
        "The monthly federal poverty guideline that Colorado's Child Care "
        "Assistance Program uses for parent fees. Section 3.111(H) sets the "
        "guideline each October 1, so January to September use the guideline "
        "published the previous calendar year."
    )
    reference = (
        # PDF pages 41-42, 84
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=41",
    )
    definition_period = MONTH
    defined_for = StateCode.CO

    def formula(spm_unit, period, parameters):
        size = spm_unit("spm_unit_size", period.this_year)
        state_group = spm_unit.household("state_group_str", period.this_year)
        instant_str = co_ccap_parameter_instant(period)
        return fpg(size, state_group, instant_str, parameters) / MONTHS_IN_YEAR
