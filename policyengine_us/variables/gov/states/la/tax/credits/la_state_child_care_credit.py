from policyengine_us.model_api import *


class la_state_child_care_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana child care credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.revenue.louisiana.gov/IndividualIncomeTax/SchoolReadinessTaxCredit"
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.la.tax.credits.child_care_expense_credit
        #calculate louisian child care credit
        
        # determine if the child care credit is less than twenty-five dollars
        
