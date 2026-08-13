from policyengine_us.model_api import *


class il_ccap_max_monthly_reimbursement(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = MONTH
    label = "Illinois CCAP maximum monthly base reimbursement per child"
    defined_for = "il_ccap_eligible_child"
    reference = "https://www.dhs.state.il.us/page.aspx?item=10864"

    def formula(person, period, parameters):
        daily_rate = person("il_ccap_max_daily_rate", period)
        # We do not model the 70% attendance rule, under which home providers
        # are paid approved eligible days rather than attended days.
        attending_days = max_(
            person("childcare_attending_days_per_month", period.this_year),
            0,
        )
        return daily_rate * attending_days
