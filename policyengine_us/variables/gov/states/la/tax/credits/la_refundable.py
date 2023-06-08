from policyengine_us.model_api import *




class la_child_expense_tax_credits_refundable(Variable):
   value_type = float
   entity = TaxUnit
   label = "Louisiana_refundable_child_expense_tax_credits"
   unit = USD
   definition_period = YEAR
   reference = "https://www.revenue.louisiana.gov/IndividualIncomeTax/SchoolReadinessTaxCredit"
   defined_for = StateCode.LA


   def formula(tax_unit, period, parameters):
       p = parameters(period).gov.states.la.tax.credits.child_care_expense_credit
       # determine if it is nonrefundable
       us_agi = tax_unit("adjusted_gross_income", period)
       agi_eligible = us_agi <=p.threshold
       # determine LA nonrefundable amount
       quality_rating = tax_unit("quality_rating_of_child_care_facility", period)
       la_child_expense_tax_credits = us_agi * p.refundable.calc(quality_rating)
       return la_child_expense_tax_credits
