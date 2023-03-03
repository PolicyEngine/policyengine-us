from policyengine_us.model_api import *


class co_tanf_countable_gross_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Colorado TANF countable gross unearned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.co.cdhs.tanf.income
        # Sum unearned sources, plus child support if not currently enrolled.
        gross_unearned = add(spm_unit, period, p.unearned)
        child_support = add(spm_unit, period, ["child_support_received"])
        enrolled = spm_unit("is_tanf_enrolled", period)
        return gross_unearned + where(enrolled, 0, child_support)
