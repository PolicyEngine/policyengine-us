from policyengine_us.model_api import *


class wa_wccc_in_home_relative_hourly_rate(Variable):
    value_type = float
    entity = Person
    label = "Washington WCCC license-exempt in-home and relative hourly rate"
    unit = USD
    definition_period = MONTH
    defined_for = "wa_wccc_eligible_child"
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0240"

    def formula(person, period, parameters):
        return parameters(period).gov.states.wa.dcyf.wccc.rates.in_home_relative
