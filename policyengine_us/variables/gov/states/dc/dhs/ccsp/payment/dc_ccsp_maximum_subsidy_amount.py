from policyengine_us.model_api import *


class dc_ccsp_maximum_subsidy_amount(Variable):
    value_type = float
    entity = Person
    label = (
        "DC Child Care Subsidy Program (CCSP) maximum subsidy amount per child"
    )
    unit = USD
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/FY25%20Subsidy%20Reimbursement%20Rates%20English.pdf#page=2"
    definition_period = MONTH
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        p = parameters(period).gov.states.dc.dhs.ccsp.reimbursement_rates
        childcare_provider = person(
            "dc_ccsp_childcare_provider_category", period
        )
        child_category = person("dc_ccsp_child_category", period)
        schedule_type = person("dc_ccsp_schedule_type", period)
        uncapped_payment_per_day = p[childcare_provider][child_category][
            schedule_type
        ]
        attending_days_per_month = person(
            "dc_ccsp_attending_days_per_month", period
        )
        return uncapped_payment_per_day * attending_days_per_month
