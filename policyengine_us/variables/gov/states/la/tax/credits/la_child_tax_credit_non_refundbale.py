from policyengine_us.model_api import *




class la_child_expense_tax_credits_nonrefundable(Variable):
   value_type = float
   entity = TaxUnit
   label = "Louisiana non refundable Child Expense Tax credit"
   unit = USD
   definition_period = YEAR
   reference = "https://www.revenue.louisiana.gov/IndividualIncomeTax/SchoolReadinessTaxCredit"
   defined_for = StateCode.LA


   def formula(tax_unit, period, parameters):
       p = parameters(period).gov.states.la.tax.credits.child_care_expense_credit
       # determine LA nonrefundable amount
       quality_rating = tax_unit("quality_rating_of_child_care_facility", period)
       return us_agi * p.nonrefundable.calc(quality_rating)
       
