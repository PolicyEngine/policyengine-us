from policyengine_us.model_api import *


class ma_tafdc_countable_earned_income(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) countable earned income"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-281"  # (A)&(B)
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        # This variable is used for the TAFDC benefit amount calculation
        # The variable is computed yearly to account for the 100% disregard for the first 6 months of the year
        p = parameters(
            period
        ).gov.states.ma.dta.tcap.tafdc.earned_income_disregard
        total_earned_income = person("ma_tcap_gross_earned_income", period)
        # fully disregard for 6 months
        full_disregard_eligible = person(
            "ma_tafdc_full_earned_income_disregard_eligible", period
        )
        full_disregard = (
            total_earned_income
            - total_earned_income * p.full_disregard.percentage
        ) * p.full_disregard.applicable_months
        remaining_months = MONTHS_IN_YEAR - p.full_disregard.applicable_months
        # The partially disregarded earned income is either applied for 6 months if the unit received
        # the full disregard or for the entire year if the unit did not receive the full disregard.
        partially_disregarded_income = (
            person("ma_tafdc_partially_disregarded_earned_income", period)
            / MONTHS_IN_YEAR
        )
        last_6_months = partially_disregarded_income * remaining_months
        first_6_months = where(
            full_disregard_eligible,
            full_disregard,
            partially_disregarded_income * p.full_disregard.applicable_months,
        )
        return first_6_months + last_6_months
