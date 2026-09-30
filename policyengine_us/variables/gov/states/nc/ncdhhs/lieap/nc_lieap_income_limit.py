from policyengine_us.model_api import *


class nc_lieap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "North Carolina LIEAP annual income limit before monthly rounding"
    defined_for = StateCode.NC
    reference = "https://policies.ncdhhs.gov/wp-content/uploads/EP-300-5.1.2026.pdf#page=10,14,15,19,20"

    def formula_2026(spm_unit, period, parameters):
        p = parameters(period).gov.states.nc.ncdhhs.lieap
        person = spm_unit.members
        size = spm_unit("nc_lieap_household_size", period)
        included = person("is_citizen_or_legal_immigrant", period)
        elderly = spm_unit.any((person("age", period) >= p.elderly_age) & included)
        # The 150% disability pathway also requires DAAS service receipt, which
        # existing inputs do not identify. Do not infer it from generic disability.
        rate = where(elderly, p.special_income_limit, p.income_limit)
        fpg_year = period.start.year - int(p.fpg_year_lag)
        fpg = parameters(f"{fpg_year}-01-01").gov.hhs.fpg
        state_group = spm_unit.household("state_group_str", period)
        amount = fpg.first_person[state_group] + fpg.additional_person[
            state_group
        ] * max_(size - 1, 0)
        # Keep the unrounded amount: the published eligibility and payment-band
        # tables each round their own monthly threshold to the nearest dollar.
        return where(size > 0, amount * rate, 0)
