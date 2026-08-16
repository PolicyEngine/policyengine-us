from policyengine_us.model_api import *


class is_head_start_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Early Head Start or Head Start income eligible"
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-45/subtitle-B/chapter-XIII/subchapter-B/part-1302/subpart-A/section-1302.12",
        "https://www.hhs.gov/answers/programs-for-families-and-children/how-can-i-get-my-child-into-head-start/index.html",
        # The 2024 final rule (effective October 2024) lets grantees deduct
        # excessive housing costs from gross income when determining
        # eligibility.
        "https://www.federalregister.gov/documents/2024/08/21/2024-18279/supporting-the-head-start-workforce-and-consistent-quality-programming",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.head_start
        countable_income = person.tax_unit("adjusted_gross_income", period)
        # Grantees may deduct housing costs exceeding a share of gross income
        # (2024 final rule); adoption is at grantee discretion, so the
        # adjustment only applies when switched on.
        if p.housing_cost_adjustment.in_effect:
            housing_cost = person.spm_unit("housing_cost", period)
            excess_housing_cost = max_(
                housing_cost
                - p.housing_cost_adjustment.income_share_threshold * countable_income,
                0,
            )
            countable_income = countable_income - excess_housing_cost
        fpg = person.tax_unit("tax_unit_fpg", period)
        # The baseline income limit is the 1302.12(c)(1)(i) statutory floor
        # (100% of the poverty guidelines); 1302.12(d) grantees may extend it
        # to 130% by reforming the limit.
        return countable_income <= fpg * p.income_limit
