from policyengine_us.model_api import *




class la_child_expense_tax_credit(Variable):
   value_type = float
   entity = TaxUnit
   label = "Louisiana non refundable Child Expense Tax credit"
   unit = USD
   definition_period = YEAR
   reference = "https://www.revenue.louisiana.gov/IndividualIncomeTax/SchoolReadinessTaxCredit"
   defined_for = StateCode.LA


   def formula(tax_unit, period, parameters):
       p = parameters(period).gov.states.la.tax.credits.child_care_expense_credit
       # determine if it is nonrefundable or refundable
       agi
       nonrefundable=tax_unit("la_child_tax_credit_non_refundable",period)
       refundable=tax_unit("la_child_tax_credit_refundable",period)
       
       agi_eligible = us_agi > p.threshold
       
       return where(agi_eligible,nonrefundable,refundable)
       