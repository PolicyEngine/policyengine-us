from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


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
        capped_size = clip(size, 1, p.max_table_size)
        additional_people = max_(size - p.max_table_size, 0)
        guideline = fpg(
            capped_size, state_group, period, parameters, year_lag=p.fpg_year_lag
        )
        additional_guideline = (
            fpg(
                capped_size + 1,
                state_group,
                period,
                parameters,
                year_lag=p.fpg_year_lag,
            )
            - guideline
        )
        monthly_factor = p.fpg_rate / MONTHS_IN_YEAR
        monthly_limit = guideline * monthly_factor
        monthly_increment = additional_guideline * monthly_factor
        # Round the base limit and each additional-person increment separately,
        # to the nearest policy increment with ties rounded up.
        rounding = p.rounding_increment
        rounded_limit = np.floor(monthly_limit / rounding + 0.5) * rounding
        rounded_increment = np.floor(monthly_increment / rounding + 0.5) * rounding
        return (rounded_limit + additional_people * rounded_increment) * MONTHS_IN_YEAR
