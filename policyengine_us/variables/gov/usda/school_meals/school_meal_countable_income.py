from policyengine_us.model_api import *


class school_meal_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Countable income for school meals"
    documentation = "SPM unit's countable income for school meal program"
    reference = (
        "https://www.ecfr.gov/current/title-7/section-245.6#p-245.6(a)(5)(ii)",
        # PDF pages 27-29, 31-32.
        "https://opi.mt.gov/Portals/182/Page%20Files/School%20Nutrition/Meal%20Eligibility/Forms%20and%20Policy/2017eligibilitymanual.pdf#page=27",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.usda.school_meals.income
        income = add(spm_unit, period, p.sources)
        income += add(spm_unit, period, p.state_supplement_sources)
        # USDA counts each person's business and rental losses as zero.
        for source in p.business_sources:
            income += spm_unit.sum(max_(spm_unit.members(source, period), 0))
        return income
