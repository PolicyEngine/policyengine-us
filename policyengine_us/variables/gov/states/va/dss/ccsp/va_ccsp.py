from policyengine_us.model_api import *


class va_ccsp(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Virginia Child Care Subsidy Program benefit"
    definition_period = MONTH
    defined_for = "va_ccsp_eligible"
    reference = (
        "https://law.lis.virginia.gov/admincode/title8/agency20/chapter790/section40/",
        "https://ris.dls.virginia.gov/uploads/22VAC40/dibr/VDOE%20Child%20Care%20Program%20Guidance%20Manual%205.3.2023-20240822104447.pdf#page=86",
    )

    def formula(spm_unit, period, parameters):
        expenses = spm_unit("spm_unit_pre_subsidy_childcare_expenses", period)
        copay = spm_unit("va_ccsp_copay", period)
        person = spm_unit.members
        daily_mrr = person("va_ccsp_daily_mrr", period)
        attending_days = person("childcare_attending_days_per_month", period.this_year)
        monthly_mrr = spm_unit.sum(daily_mrr * attending_days)
        capped_expenses = min_(expenses, monthly_mrr)
        return max_(capped_expenses - copay, 0)
