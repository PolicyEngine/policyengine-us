from policyengine_us.model_api import *


class ma_tafdc_ssi_recipient_unearned_income_exclusion(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Massachusetts TAFDC SSI recipient" " unearned income exclusion"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts"
        "/106-CMR-704-250"
    )
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        # Section (A): All unearned income of household
        # members receiving SSI is noncountable.
        receives_ssi = person("ssi_reported", period, options=[DIVIDE]) > 0
        gross_unearned = person("ma_tcap_gross_unearned_income", period)
        return where(receives_ssi, gross_unearned, 0)
