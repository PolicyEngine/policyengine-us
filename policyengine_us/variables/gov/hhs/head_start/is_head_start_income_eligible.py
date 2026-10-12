from policyengine_us.model_api import *


class is_head_start_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Early Head Start or Head Start income eligible"
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-45/section-1302.12",
        "https://www.hhs.gov/answers/programs-for-families-and-children/how-can-i-get-my-child-into-head-start/index.html",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.head_start.income_limit
        spm_unit = person.spm_unit
        countable_income = spm_unit("head_start_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        # Income "equal to or below" the poverty line meets the statutory
        # limit (45 CFR 1302.12(c)(1)(i)); a program may also enroll families
        # whose income is "below" 130% of the poverty line (45 CFR 1302.12(d)),
        # so the discretionary limit is a strict bound.
        uses_discretionary_limit = spm_unit(
            "head_start_uses_discretionary_income_limit", period
        )
        under_statutory_limit = countable_income <= fpg * p.statutory
        under_discretionary_limit = countable_income < fpg * p.discretionary
        return where(
            uses_discretionary_limit,
            under_discretionary_limit,
            under_statutory_limit,
        )
