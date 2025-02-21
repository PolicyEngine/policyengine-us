from policyengine_us.model_api import *


class nc_scca_parent_fee(Variable):
    value_type = int
    entity = SPMUnit
    label = (
        "North Carolina Subsidized Child Care Assistance Program parent fee"
    )
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.NC
    reference = "https://policies.ncdhhs.gov/wp-content/uploads/chapter-8-parental-fees-7.pdf#page=2"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nc.ncdhhs.scca
        parent_fee_rate = p.parent_fee_rate.value

        family_monthly_income = spm_unit("nc_scca_countable_income", period)

        parent_fee = family_monthly_income * parent_fee_rate

        # Round the number and only keep the integer part
        return np.round(parent_fee).astype(int)
