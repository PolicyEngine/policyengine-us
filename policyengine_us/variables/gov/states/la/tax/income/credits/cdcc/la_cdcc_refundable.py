from policyengine_us.model_api import *


class la_cdcc_refundable(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana refundable Child and Dependent Care Credit"
    unit = USD
    definition_period = YEAR
    reference = "http://legis.la.gov/Legis/Law.aspx?d=101769"
    defined_for = "la_cdcc_refundable_eligible"

    adds = ["la_cdcc"]
