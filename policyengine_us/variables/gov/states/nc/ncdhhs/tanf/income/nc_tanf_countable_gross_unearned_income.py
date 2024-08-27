from policyengine_us.model_api import *


class nc_tanf_countable_gross_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Carolina TANF countable gross unearned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NC

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nc.ncdhhs.tanf.income
        # Sum unearned sources, plus child support if not currently enrolled.
        gross_unearned = add(spm_unit, period, p.unearned)
        child_support = add(spm_unit, period, ["child_support_received"])
        tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        additional_amount = where(tanf_enrolled, 0, child_support)
        return gross_unearned + additional_amount
