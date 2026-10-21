from policyengine_us.model_api import *


class ca_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "California other additions to federal AGI"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    documentation = (
        "California other additions to federal adjusted gross income reported on "
        "Schedule CA (540), Part I, Section B, Line 8z (Other income, Column C), "
        "entered as a positive amount."
    )
    reference = "https://www.ftb.ca.gov/forms/2025/2025-540-ca-instructions.html"
