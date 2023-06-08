from policyengine_us.model_api import *




class quality_rating_of_child_care_facility(Variable):
   value_type = float
   entity = TaxUnit
   label = "Louisiana quality rating of child care facility"
   definition_period = YEAR
   reference = "https://www.revenue.louisiana.gov/IndividualIncomeTax/SchoolReadinessTaxCredit"
   