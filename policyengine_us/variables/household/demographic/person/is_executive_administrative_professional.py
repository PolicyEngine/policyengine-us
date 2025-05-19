from policyengine_us.model_api import *


class is_executive_administrative_professional(Variable):
    value_type = bool
    entity = Person
    label = "is employed in a bona fide executive, administrative, or professional capacity"
    reference = "https://www.law.cornell.edu/uscode/text/29/213 ; https://www.congress.gov/crs-product/IF12480"
    definition_period = YEAR
