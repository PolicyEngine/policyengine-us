from policyengine_us.model_api import *


class snap_child_support_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP child support expense"
    unit = USD
    documentation = (
        "Child support payments treated as expenses for SNAP purposes, "
        "with prorated-disqualified members' contributions reduced per "
        "7 CFR 273.11(c)(2). For eligible and entirety-disqualified "
        "members (c1), the full expense counts; for prorated-"
        "disqualified members (c2/c3), only the eligible members' "
        "share of their expense counts."
    )
    definition_period = MONTH
    reference = ("https://www.law.cornell.edu/cfr/text/7/273.11#c_2",)

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        expense = person("child_support_expense", period)
        share = person("snap_income_share", period)
        return spm_unit.sum(expense * share)
