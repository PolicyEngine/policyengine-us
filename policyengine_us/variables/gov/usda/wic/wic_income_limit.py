from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class wic_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    unit = USD
    label = "WIC income limit"
    documentation = "Annual income limit for WIC direct income eligibility"
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1786#d_2_A_i",
        "https://www.law.cornell.edu/cfr/text/7/246.7#d_2_vii",
        "https://www.fns.usda.gov/wic/income-eligibility-guidelines-2025-26",
        # PDF pages 1-3.
        "https://www.govinfo.gov/content/pkg/FR-2016-03-18/pdf/2016-06222.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        spm_unit_size = spm_unit("spm_unit_size", period.this_year)
        current_pregnancies = spm_unit.sum(
            spm_unit.members("current_pregnancies", period.this_year)
        )
        wic_unit_size = spm_unit_size + current_pregnancies

        state_group = spm_unit.household("state_group_str", period.this_year)
        wic_state_group = np.where(
            np.isin(state_group, ("AK", "HI")),
            state_group,
            "CONTIGUOUS_US",
        )

        year = period.start.year
        month = period.start.month
        hhs_guideline_year = year if month >= 7 else year - 1
        annual_fpg = fpg(
            wic_unit_size,
            wic_state_group,
            f"{hhs_guideline_year}-01-01",
            parameters,
        )
        reduced_school_meal_limit = parameters(
            period
        ).gov.usda.school_meals.income.limit.REDUCED
        return np.ceil(annual_fpg * reduced_school_meal_limit)
