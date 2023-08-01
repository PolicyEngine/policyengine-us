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
        ).gov.states.la.tax.credits.child_care_expense_credit.rate

        #calculate louisian child care credit
        us_agi = tax_unit("adjusted_gross_income", period)
        federal_credit = tax_unit("",period)
        child_care_credit = federal_credit * p.la_state_credit.calc(us_agi)

        #check if agi is more than sixty-thousand dollars
        credit_income_threshold = us_agi > p.income_threshold_for_credit

        #if agi is more than sixty-thousand dollars, check if the state child care credit is less than twenty-five dollars
        credit_threshold = (child_care_credit > p.credit_threshold) * credit_income_threshold

        return where(credit_threshold, 25, child_care_credit)
