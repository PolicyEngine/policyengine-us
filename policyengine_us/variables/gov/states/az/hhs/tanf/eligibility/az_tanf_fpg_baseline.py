from policyengine_us.model_api import *


class az_tanf_fpg_baseline(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona TANF payment standard FPG baseline"
    unit = USD
    definition_period = YEAR
    reference = "https://www.azleg.gov/ars/46/00207-01.htm"
    defined_for = StateCode.AZ

    def formula(spm_unit, period, parameters):
        # Arizona uses 1992 FPG values for payment standard calculations
        instant_str = "1992-01-01"
        household_size = spm_unit("spm_unit_size", period)
        state_group = spm_unit.household("state_group_str", period)

        p_fpg = parameters(instant_str).gov.hhs.fpg
        p1 = p_fpg.first_person[state_group]
        pn = p_fpg.additional_person[state_group]

        return p1 + pn * (household_size - 1)
