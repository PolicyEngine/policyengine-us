from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class ca_liheap_income_group(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "California LIHEAP poverty group"
    defined_for = StateCode.CA
    reference = "https://www.csd.ca.gov/Shared%20Documents/2026-Final-LIHEAP-State-Plan.pdf#page=184"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.csd.liheap.income
        size = spm_unit("ca_liheap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(
            max_(size, 1), state_group, period, parameters, year_lag=p.fpg_year_lag
        )
        income = spm_unit("ca_liheap_countable_income", period)
        # Compare integer cents to preserve published inclusive boundaries
        # after annual monetary inputs have been stored as float32.
        monthly_income_cents = np.rint(
            income.astype(float) / MONTHS_IN_YEAR / p.monthly_rounding_increment
        )
        group = 1
        for rate in p.poverty_group_rates:
            threshold_cents = np.floor(
                guideline * rate / MONTHS_IN_YEAR / p.monthly_rounding_increment + 0.5
            )
            group = group + (monthly_income_cents > threshold_cents)
        above_smi = income > spm_unit("ca_liheap_income_limit", period)
        return where(above_smi, len(p.poverty_group_rates) + 1, group)
