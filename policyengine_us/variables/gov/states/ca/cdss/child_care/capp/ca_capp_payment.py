from policyengine_us.model_api import *


class ca_capp_payment(Variable):
    value_type = float
    entity = Person
    label = "California Alternative Payment Program payment"
    unit = USD
    definition_period = MONTH
    defined_for = "ca_capp_eligible"
    reference = "https://cdrv.org/cdr-programs-and-services/california-work-opportunity-and-responsibility-to-kids-calworks-alternative-payment-programs/"

    def formula(person, period, parameters):
        # CAPP uses same RMR payment structure as CalWORKs child care
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

        gross_payment = min_(
            payment_standard * time_coefficient * payment_factor,
            childcare_expenses,
        )
        return gross_payment
