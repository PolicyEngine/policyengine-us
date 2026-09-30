from policyengine_us.model_api import *


class nc_lieap_earned_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "North Carolina LIEAP earned income per person"
    defined_for = StateCode.NC
    reference = "https://policies.ncdhhs.gov/wp-content/uploads/EP-300-5.1.2026.pdf#page=10,11,12,13,15,16,17"

    def formula(person, period, parameters):
        countable = person("snap_countable_earner", period.first_month)
        # Existing net self-employment income approximates receipts less allowed
        # costs. No second business-expense deduction or new input is introduced.
        earnings = max_(person("employment_income", period), 0) + max_(
            person("self_employment_income", period), 0
        )
        # Section 300.09 B.3 includes rental income in the work deduction.
        return earnings * countable + max_(person("rental_income", period), 0)
