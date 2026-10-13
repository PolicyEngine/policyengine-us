from policyengine_us.model_api import *


class ca_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "California other additions to federal AGI"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    documentation = "Other additions to federal adjusted gross income reported on California Schedule CA (540), Part I, Section B, Line 8."
    reference = "https://www.ftb.ca.gov/forms/2024/2024-540-ca-instructions.html"
