from policyengine_us.model_api import *


class wa_wccc_center_daily_rate(Variable):
    value_type = float
    entity = Person
    label = "Washington WCCC licensed center daily reimbursement rate"
    unit = USD
    definition_period = MONTH
    defined_for = "wa_wccc_eligible_child"
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0200"

    def formula(person, period, parameters):
        rates = parameters(period).gov.states.wa.dcyf.wccc.rates.center
        region = person.household("wa_wccc_center_region", period)
        age_group = person("wa_wccc_center_age_group", period)
        time_category = person("wa_wccc_center_time_category", period)
        return rates[region][age_group][time_category]
