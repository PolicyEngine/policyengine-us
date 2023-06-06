from policyengine_us.model_api import *




class la_childexpensetaxcredits_nonrefundable(Variable):
   value_type = float
   entity = TaxUnit
   label = "Louisiana Child Expense Tax credits"
   unit = star
   definition_period = YEAR
   reference = https://www.revenue.louisiana.gov/IndividualIncomeTax/SchoolReadinessTaxCredit
   defined_for = StateCode.LA


   def formula(tax_unit, period, parameters):
       p = parameters(period).gov.states.la.tax.credits
       # determine if it is nonrefundable
       us_agi = tax_unit("adjusted_gross_income", period)
       agi_eligible = us_agi > p.threshold
       # determine LA nonrefundable amount
       us_qualityrating = tax_unit("quality rating", period)
       la_childexpense = us_qualityrating * p.nonrefundable.nonrefundable
       return la_childexpense
