from policyengine_us.model_api import *


class ms_wd_premium(Variable):
    value_type = float
    entity = Person
    label = "Mississippi Working Disabled monthly premium"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://medicaid.ms.gov/wp-content/uploads/2026/03/Appendix-A-5-WD-Premiums-for-March-2026.pdf#page=1",
        "https://medicaid.ms.gov/wp-content/uploads/2026/03/Appendix-A-5-WD-Premiums-for-March-2026.pdf#page=3",
        "https://medicaid.ms.gov/medicaid-coverage/who-qualifies-for-coverage/working-disabled/",
    )
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ms.dom.wd.premium
        eligible = person("ms_wd_eligible", period)
        eligible_count = person.marital_unit.sum(eligible)
        countable_earned_income = person("ms_wd_countable_earned_income", period)
        premium_applies = (
            countable_earned_income > person("ms_wd_fpg", period) * p.fpl_threshold
        )
        marital_unit_premium = where(
            premium_applies,
            np.floor(countable_earned_income * p.rate),
            0,
        )
        return where(
            eligible & (eligible_count > 0),
            marital_unit_premium / eligible_count,
            0,
        )
