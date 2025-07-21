from policyengine_us.model_api import *


class dc_ccsp_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "DC Child Care Subsidy Program (CCSP) copay"
    definition_period = MONTH
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/Sliding%20Fee%20Scale.pdf"
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.dc.dhs.ccsp.copay
        qualified_need_eligible = spm_unit(
            "dc_ccsp_qualified_need_eligible", period
        )
        countable_income = spm_unit("dc_ccsp_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        income_eligible = countable_income < fpg * p.exempted_rate
        exempted_eligible = qualified_need_eligible | income_eligible

        total_copay = add(
            spm_unit,
            period,
            [
                "dc_ccsp_first_child_copay",
                "dc_ccsp_second_child_copay",
            ],
        )

        return where(exempted_eligible, 0, total_copay)
