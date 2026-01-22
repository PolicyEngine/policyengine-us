from policyengine_us.model_api import *


class ca_calworks_stage_2_payment(Variable):
    value_type = float
    entity = Person
    label = "California CalWORKs Stage 2 child care payment"
    unit = USD
    definition_period = MONTH
    defined_for = "ca_calworks_stage_2_eligible"
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=10372.&lawCode=WIC"

    def formula(person, period, parameters):
        # Uses same RMR payment structure as Stage 1
        payment_standard = person(
            "ca_calworks_child_care_payment_standard", period
        )
        time_coefficient = person(
            "ca_calworks_child_care_time_coefficient", period
        )
        payment_factor = person(
            "ca_calworks_child_care_payment_factor", period
        )
        childcare_expenses = person("pre_subsidy_childcare_expenses", period)

        return min_(
            payment_standard * time_coefficient * payment_factor,
            childcare_expenses,
        )
