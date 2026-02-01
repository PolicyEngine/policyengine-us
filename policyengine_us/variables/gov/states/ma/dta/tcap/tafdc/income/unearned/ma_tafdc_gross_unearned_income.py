from policyengine_us.model_api import *


class ma_tafdc_gross_unearned_income(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = (
        "Massachusetts TAFDC gross unearned income"
        " after noncountable exclusions"
    )
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts"
        "/106-CMR-704-250"
    )
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        gross = person("ma_tcap_gross_unearned_income", period)
        # Section (A): SSI recipient unearned income
        ssi_exclusion = person(
            "ma_tafdc_ssi_recipient_unearned_income_exclusion",
            period,
        )
        # Section (B): Lump sum income exclusion
        lump_sum_exclusion = person(
            "ma_tafdc_lump_sum_income_exclusion", period
        )
        total_exclusion = ssi_exclusion + lump_sum_exclusion
        return max_(0, gross - total_exclusion)
