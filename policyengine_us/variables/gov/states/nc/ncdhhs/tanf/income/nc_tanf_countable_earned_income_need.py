from policyengine_us.model_api import *


class nc_tanf_countable_earned_income_need(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Carolina TANF total countable income for need determination"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NC

    def formula(spm_unit, period, parameters):
        gross_earnings = spm_unit(
            "nc_tanf_countable_gross_earned_income", period
        )
        p = parameters(period).gov.states.nc.ncdhhs.tanf.income.earned_exclusion
        enrolled = spm_unit("is_tanf_enrolled", period)
        annual_flat_exclusion = p.flat * MONTHS_IN_YEAR
        # needs modify
        return where(
            enrolled,
            # For enrolled participants, Colorado applies only a percent exclusion.
            gross_earnings * (1 - p.percent),
            # For new enrollees, Colorado applies only a flat exclusion.
            max_(gross_earnings - annual_flat_exclusion, 0),
        )
