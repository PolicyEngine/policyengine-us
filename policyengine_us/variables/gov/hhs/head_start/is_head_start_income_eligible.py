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
        # The statutory limit is 100% of the poverty guidelines
        # (45 CFR 1302.12(c)(1)(i)); a program may enroll families up to
        # 130% under 45 CFR 1302.12(d).
        uses_discretionary_limit = spm_unit(
            "head_start_uses_discretionary_income_limit", period
        )
        limit = where(uses_discretionary_limit, p.discretionary, p.statutory)
        return countable_income <= fpg * limit
