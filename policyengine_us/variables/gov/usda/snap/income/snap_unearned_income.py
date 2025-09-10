from policyengine_us.model_api import *


class snap_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "SNAP unearned income"
    documentation = "Unearned income for calculating the SNAP benefit"
    reference = "https://www.law.cornell.edu/cfr/text/7/273.9#b_2"
    unit = USD

    def formula(spm_unit, period, parameters):
        # Get all unearned income
        unearned_income_sources = parameters(
            period
        ).gov.usda.snap.income.sources.unearned
        
        total_unearned = add(spm_unit, period, unearned_income_sources)
        
        # Subtract the portion that's from work requirement disqualified members
        # (which is calculated separately in snap_work_disqualified_unearned_income)
        disqualified_unearned = spm_unit(
            "snap_work_disqualified_unearned_income", period
        )
        
        return total_unearned - disqualified_unearned
