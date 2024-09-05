from policyengine_us.model_api import *


class la_quality_rating_of_child_care_facility(Variable):
    value_type = int
    entity = Person
    label = "Quality rating of child care facility for the Louisiana school readiness tax credit"
    definition_period = YEAR
    defined_for = StateCode.LA
    reference = "https://www.revenue.louisiana.gov/IndividualIncomeTax/SchoolReadinessTaxCredit"
