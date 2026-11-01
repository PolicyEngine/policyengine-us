from policyengine_us.model_api import *


class ca_la_ez_save(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH
    label = "Los Angeles EZ-SAVE program"
    documentation = (
        "The Los Angeles Department of Water and Power's EZ-SAVE program "
        "discounts electricity bills for income-qualified customers. The "
        "department serves the City of Los Angeles rather than the whole "
        "county, but the model has no utility-territory input, so it applies "
        "EZ-SAVE to every eligible Los Angeles County household."
    )
    reference = (
        # Schedule R-1, Section 2.d: Rate D is Rate A less the Low-Income Credit.
        "https://www.ladwp.com/sites/default/files/documents/LADWP_Electric_Rates.pdf#page=4",
        # The subsidy should not exceed the customer's electric bill.
        "https://www.ladwp.com/account/customer-service/electric-rates/residential-rates#ez-save",
    )
    defined_for = "ca_la_ez_save_eligible"

    def formula(household, period, parameters):
        electricity_expense = add(
            household, period, ["pre_subsidy_electricity_expense"]
        )
        p = parameters(period).gov.local.ca.la.dwp.ez_save
        uncapped_amount = p.amount
        return min_(electricity_expense, uncapped_amount)
