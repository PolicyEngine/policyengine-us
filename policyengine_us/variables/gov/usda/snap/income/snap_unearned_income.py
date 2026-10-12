from policyengine_us.model_api import *


class snap_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "SNAP unearned income"
    documentation = "Unearned income for calculating the SNAP benefit"
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.9#b_2",
        "https://www.law.cornell.edu/cfr/text/7/273.11#c",
    )
    unit = USD

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        unearned = person("snap_unearned_income_person", period)
        share = person("snap_income_counted_share", period)
        p = parameters(period).gov.usda.snap.income.sources
        unit_level = add(spm_unit, period, p.unearned_spm_unit)
        return spm_unit.sum(unearned * share) + unit_level
