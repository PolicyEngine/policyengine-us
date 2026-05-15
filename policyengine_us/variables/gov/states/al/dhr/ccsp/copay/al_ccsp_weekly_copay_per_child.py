from policyengine_us.model_api import *


class al_ccsp_weekly_copay_per_child(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Alabama CCSP weekly per-child parental fee"
    definition_period = MONTH
    defined_for = StateCode.AL
    reference = (
        "Alabama Child Care Fact Sheet (Parental Fee Chart)",
        "https://dhr.alabama.gov/wp-content/uploads/2024/01/Child-Care-Fact-Sheet-2024.pdf",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.al.dhr.ccsp.copay
        monthly_income = spm_unit("al_ccsp_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period.this_year)
        # Compare monthly income against the monthly federal poverty
        # guideline to compute the FPL ratio.
        monthly_fpg = fpg / MONTHS_IN_YEAR
        fpl_ratio = where(monthly_fpg > 0, monthly_income / monthly_fpg, 0)

        enrolled = spm_unit("al_ccsp_enrolled", period)
        initial_fee = p.initial_fee_by_fpl.calc(fpl_ratio)
        continuing_fee = p.continuing_fee_by_fpl.calc(fpl_ratio)
        # Continuing families above 180% FPL use the continuing fee scale;
        # all other families use the initial fee scale.
        return where(enrolled, continuing_fee, initial_fee)
