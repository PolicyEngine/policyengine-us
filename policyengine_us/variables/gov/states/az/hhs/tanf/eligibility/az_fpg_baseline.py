from policyengine_us.model_api import *

class az_fpg_baseline(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona Cash Assistance Payment Standard fpg Baseline"
    definition_period = YEAR
    reference = "https://des.az.gov/services/child-and-family/cash-assistance/cash-assistance-ca-income-eligibility-guidelines"
    defined_for = StateCode.AZ

    def formula(spm_unit, period, parameters):
        fpg_year = f"1992-01-01"
        household_size = spm_unit("az_countable_household_size", period)
        print(household_size)
        state_group = spm_unit.household("state_group_str", period)
        p_fpg = parameters(fpg_year).gov.hhs.fpg
        p1 = p_fpg.first_person[state_group]
        pn = p_fpg.additional_person[state_group]
        fpg_baseline = p1 + pn * (household_size - 1)
        return fpg_baseline/MONTHS_IN_YEAR