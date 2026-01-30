from policyengine_us.model_api import *


class nc_tanf_need_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Carolina TANF need standard"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NC

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nc.ncdhhs.tanf.need_standard
        household_size = spm_unit("nc_tanf_household_size", period)
        capped_household_size = clip(
            household_size, 1, p.max_table_size
        ).astype(int)
        additional_people = household_size - capped_household_size
        base = p.main[capped_household_size]
        additional_maximum_benefit = p.additional_person * additional_people
        monthly_amount = base + additional_maximum_benefit
        return monthly_amount * MONTHS_IN_YEAR
