from policyengine_us.model_api import *


class wic_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    unit = USD
    label = "WIC income limit"
    documentation = "Annual income limit for WIC direct income eligibility"
    reference = [
        "https://www.law.cornell.edu/uscode/text/42/1786#d_2_A_i",
        "https://www.fns.usda.gov/wic/income-eligibility-guidelines-2025-26",
    ]

    def formula(spm_unit, period, parameters):
        spm_unit_size = spm_unit("spm_unit_size", period.this_year)
        pregnant = spm_unit.any(spm_unit.members("is_pregnant", period))
        wic_unit_size = spm_unit_size + pregnant

        state_group = spm_unit.household("state_group_str", period.this_year)
        wic_state_group = np.where(
            np.isin(state_group, ("AK", "HI")),
            state_group,
            "CONTIGUOUS_US",
        )

        year = period.start.year
        month = period.start.month
        hhs_guideline_year = year if month >= 7 else year - 1
        p_fpg = parameters(f"{hhs_guideline_year}-01-01").gov.hhs.fpg
        first_person = p_fpg.first_person[wic_state_group]
        additional_person = p_fpg.additional_person[wic_state_group]
        fpg = first_person + additional_person * (wic_unit_size - 1)
        reduced_school_meal_limit = parameters(
            period
        ).gov.usda.school_meals.income.limit.REDUCED
        return np.ceil(fpg * reduced_school_meal_limit)
