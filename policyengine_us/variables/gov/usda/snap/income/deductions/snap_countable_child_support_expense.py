from policyengine_us.model_api import *


class snap_countable_child_support_expense(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "SNAP countable child support expense"
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2014#e_4",
        "https://www.law.cornell.edu/cfr/text/7/273.11#c_2_iii",
    )
    unit = USD

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        expense = person("child_support_expense", period)
        share = person("snap_income_counted_share", period)
        return spm_unit.sum(expense * share)
