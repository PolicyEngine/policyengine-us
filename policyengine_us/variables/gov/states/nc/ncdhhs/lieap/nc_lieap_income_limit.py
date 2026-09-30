from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class nc_lieap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "North Carolina LIEAP annual income limit before monthly rounding"
    defined_for = StateCode.NC
    reference = "https://policies.ncdhhs.gov/wp-content/uploads/EP-300-5.1.2026.pdf#page=10,14,15,19,20"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nc.ncdhhs.lieap
        person = spm_unit.members
        size = spm_unit("nc_lieap_household_size", period)
        included = person("is_citizen_or_legal_immigrant", period)
        special = spm_unit.any(
            (
                (person("age", period) >= p.elderly_age)
                | person("nc_lieap_is_daas_disabled", period)
            )
            & included
        )
        rate = where(special, p.special_income_limit, p.income_limit)
        state_group = spm_unit.household("state_group_str", period)
        amount = fpg(
            max_(size, 1), state_group, period, parameters, year_lag=p.fpg_year_lag
        )
        # Keep the unrounded amount: the published eligibility and payment-band
        # tables each round their own monthly threshold to the nearest dollar.
        return where(size > 0, amount * rate, 0)
