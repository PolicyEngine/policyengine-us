from policyengine_us.model_api import *


class ma_tafdc_gross_earned_income(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = (
        "Massachusetts TAFDC gross earned income"
        " after noncountable exclusions"
    )
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts"
        "/106-CMR-704-250"
    )
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        gross = person("ma_tcap_gross_earned_income", period)
        # Section (A): SSI recipient earned income
        ssi_exclusion = person(
            "ma_tafdc_ssi_recipient_earned_income_exclusion",
            period,
        )
        # Section (U): Dependent child earned income
        child_exclusion = person(
            "ma_tafdc_dependent_child_earned_income_exclusion",
            period,
        )
        # Take the max to avoid double-counting when a child
        # both receives SSI and qualifies under Section (U).
        total_exclusion = max_(ssi_exclusion, child_exclusion)
        return max_(0, gross - total_exclusion)
