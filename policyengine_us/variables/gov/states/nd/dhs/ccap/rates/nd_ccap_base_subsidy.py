from policyengine_us.model_api import *


class nd_ccap_base_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "North Dakota CCAP base subsidy"
    definition_period = MONTH
    defined_for = "nd_ccap_eligible"
    reference = "https://www.nd.gov/dhs/policymanuals/40028/40028.htm"

    def formula(spm_unit, period, parameters):
        # The base subsidy is the lesser of the summed per-child state maximum
        # rates and the family's billed child care expenses, minus the monthly
        # co-payment, floored at zero (400-28-100-05). The special-needs +10%
        # is already folded into nd_ccap_state_max_rate, so it sits inside the
        # expense cap. The expense cap pools the per-child maximum rates across
        # the unit (the IN / RI / MA convention), because billed expenses are a
        # single SPM-unit input.
        # Registration fees (annual enrollment fees CCAP pays directly to
        # C/E/K/M/F/G/H providers, up to $150 per child per calendar year,
        # 400-28-130-15-15) are not modeled: they are a separate provider
        # payment outside the monthly care subsidy, and we don't track whether a
        # provider charges a registration fee or its amount at the moment.
        maximum_monthly_rate = add(spm_unit, period, ["nd_ccap_state_max_rate"])
        pre_subsidy_childcare_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        capped_expenses = min_(pre_subsidy_childcare_expenses, maximum_monthly_rate)
        copay = spm_unit("nd_ccap_copay", period)
        return max_(capped_expenses - copay, 0)
