from policyengine_us.model_api import *


class mn_mfip_child_support_income_exclusion(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP child support income exclusion"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256P.06#stat.256P.06.3"
    )
    defined_for = StateCode.MN

    def formula(spm_unit, period, parameters):
        # Per MN Stat. 256P.06, Subd. 3:
        # Child support up to $100 (1 child) or $200 (2+ children) is excluded.
        p = parameters(
            period
        ).gov.states.mn.dcyf.mfip.income.deductions.child_support
        child_support = add(spm_unit, period, ["child_support_received"])
        children = spm_unit("spm_unit_count_children", period.this_year)
        max_disregard = p.calc(children)
        return min_(child_support, max_disregard)
