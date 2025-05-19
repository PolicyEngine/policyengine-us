from policyengine_us.model_api import *


class is_eligible_for_fsla_overtime(Variable):
    value_type = bool
    entity = Person
    label = "is eligible for overtime pay"
    reference = "https://www.law.cornell.edu/cfr/text/29/541.600 ; https://www.law.cornell.edu/uscode/text/29/213"
    definition_period = YEAR

    def formula_2014(person, period, parameters):
        # Get the applicable threshold
        applicable_threshold = person("fsla_overtime_salary_threshold", period)

        # Check payment method and income
        is_paid_hourly = person("is_paid_hourly", period)
        employment_income = person("employment_income", period)

        # The worker is exempt if:
        # 1. Their income exceeds the threshold corresponding to their exemption category
        # 2. They're not paid hourly
        is_exempt = (employment_income >= applicable_threshold) & (
            ~is_paid_hourly
        )

        # Return True if eligible for overtime protection, False if exempt
        return ~is_exempt
