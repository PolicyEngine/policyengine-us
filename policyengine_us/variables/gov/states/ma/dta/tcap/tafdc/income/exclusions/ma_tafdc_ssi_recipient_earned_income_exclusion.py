from policyengine_us.model_api import *


class ma_tafdc_ssi_recipient_earned_income_exclusion(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Massachusetts TAFDC SSI recipient" " earned income exclusion"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts"
        "/106-CMR-704-250"
    )
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        # Section (A): All earned income of household members
        # receiving SSI is noncountable.
        receives_ssi = person("ssi_reported", period, options=[DIVIDE]) > 0
        gross_earned = person("ma_tcap_gross_earned_income", period)
        return where(receives_ssi, gross_earned, 0)
