from policyengine_us.model_api import *


class nc_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Carolina TANF"
    unit = USD
    definition_period = YEAR
    defined_for = "nc_tanf_eligible"

    def formula(spm_unit, period, parameters):
        payment_percentage = parameters(
            period
        ).gov.states.nc.ncdhhs.tanf.need_standard.monthly_percentage
        need_standard = spm_unit("nc_tanf_need_standard", period)
        income = add(
            spm_unit,
            period,
            [
                "nc_tanf_countable_earned_income_grant_standard",
                "nc_tanf_countable_gross_unearned_income",
            ],
        )

        return max_((need_standard - income) * payment_percentage, 0)
