from policyengine_us.model_api import *


class ca_calworks_child_care_payment(Variable):
    value_type = float
    entity = Person
    label = "California CalWORKs Child Care payment"
    unit = USD
    definition_period = MONTH
    defined_for = "ca_calworks_child_care_eligible"

    def formula(person, period, parameters):
        payment_standard = person(
            "ca_calworks_child_care_payment_standard", period
        )
        # Scale up hourly/daily/weekly values to month.
        time_coefficient = person(
            "ca_calworks_child_care_time_coefficient", period
        )
        # Payment factor is a multiplier for disability, weekend service, etc.
        payment_factor = person(
            "ca_calworks_child_care_payment_factor", period
        )
        childcare_expenses = person("pre_subsidy_childcare_expenses", period)

        return min_(
            payment_standard * time_coefficient * payment_factor,
            childcare_expenses,
        )
