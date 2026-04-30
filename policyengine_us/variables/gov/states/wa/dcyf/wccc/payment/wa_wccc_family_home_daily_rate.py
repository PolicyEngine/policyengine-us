from policyengine_us.model_api import *


class wa_wccc_family_home_daily_rate(Variable):
    value_type = float
    entity = Person
    label = "Washington WCCC licensed family home daily reimbursement rate"
    unit = USD
    definition_period = MONTH
    defined_for = "wa_wccc_eligible_child"
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0205"

    def formula(person, period, parameters):
        rates = parameters(period).gov.states.wa.dcyf.wccc.rates.family_home
        region = person.household("wa_wccc_region", period)
        age_group = person("wa_wccc_family_home_age_group", period)
        time_category = person("wa_wccc_family_home_time_category", period)
        return rates[region][age_group][time_category]
