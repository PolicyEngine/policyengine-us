from policyengine_us.model_api import *
from policyengine_us.tools.liheap import calculate_liheap_fpg_income_limit


class ks_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Kansas LIEAP annualized income limit"
    defined_for = StateCode.KS
    reference = (
        "https://content.dcf.ks.gov/ees/KEESM/Robo10-24/Robo_10_01_24/keesm13360.htm",
        "https://content.dcf.ks.gov/ees/KEESM/Robo01-26/Robo_01_01_26/keesm13360.htm",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ks.dcf.liheap.eligibility
        size = spm_unit("ks_liheap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        return calculate_liheap_fpg_income_limit(
            size, state_group, period, parameters, p
        )
