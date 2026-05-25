from policyengine_us.model_api import *


class snap_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "SNAP unearned income"
    documentation = "Unearned income for calculating the SNAP benefit"
    reference = "https://www.law.cornell.edu/cfr/text/7/273.9#b_2"
    unit = USD

    def formula(spm_unit, period):
        person = spm_unit.members
        income = person("snap_unearned_income_person", period)
        fraction = person("snap_work_requirement_income_proration_fraction", period)
        return spm_unit.sum(income * fraction)
