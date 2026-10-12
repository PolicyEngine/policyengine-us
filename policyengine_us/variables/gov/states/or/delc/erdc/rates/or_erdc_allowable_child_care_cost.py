from policyengine_us.model_api import *


class or_erdc_allowable_child_care_cost(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    unit = USD
    label = "Oregon ERDC allowable child care cost"
    defined_for = StateCode.OR
    reference = (
        "https://secure.sos.state.or.us/oard/view.action?ruleNumber=414-175-0075"
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        eligible_child = person("or_erdc_eligible_child", period)
        expenses = person("pre_subsidy_childcare_expenses", period)
        maximum_rate = person("or_erdc_maximum_monthly_rate", period)
        return spm_unit.sum(where(eligible_child, min_(expenses, maximum_rate), 0))
