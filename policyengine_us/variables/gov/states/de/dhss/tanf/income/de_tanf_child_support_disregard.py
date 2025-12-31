from policyengine_us.model_api import *


class de_tanf_child_support_disregard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Delaware TANF child support disregard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/delaware/"
        "16-Del-Admin-Code-SS-4000-4008",
        "https://dhss.delaware.gov/dss/tanf/",
    )
    defined_for = StateCode.DE

    def formula(spm_unit, period, parameters):
        # Per DSSM 4008: First $50 of child support is disregarded
        p = parameters(period).gov.states.de.dhss.tanf.income.deductions

        child_support = add(spm_unit, period, ["child_support_received"])

        return min_(child_support, p.child_support.amount)
