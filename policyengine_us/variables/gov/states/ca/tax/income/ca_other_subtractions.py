from policyengine_us.model_api import *


class ca_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "California other subtractions from federal AGI"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    documentation = "Other subtractions from federal adjusted gross income reported on California Schedule CA (540), Part I, Section B, Line 22."
    reference = "https://www.ftb.ca.gov/forms/2024/2024-540-ca-instructions.html"
