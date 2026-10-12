from policyengine_us.model_api import *


class or_erdc(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    unit = USD
    label = "Oregon Employment Related Day Care benefit amount"
    defined_for = "or_erdc_eligible"
    reference = (
        "https://secure.sos.state.or.us/oard/view.action?ruleNumber=414-175-0075"
    )

    def formula(spm_unit, period, parameters):
        allowable_cost = spm_unit("or_erdc_allowable_child_care_cost", period)
        copay = spm_unit("or_erdc_copay", period)
        return max_(allowable_cost - copay, 0)
