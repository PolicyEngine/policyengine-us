from policyengine_us.model_api import *


class nd_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Dakota other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ND
    documentation = (
        "North Dakota other subtractions from federal taxable income reported on "
        "Form ND-1, Line 16 (Total other subtractions from Schedule ND-1SA), entered as a "
        "positive amount, excluding subtractions PolicyEngine calculates separately."
    )
    reference = "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2023-iit/form-nd-1-2023.pdf#page=1"
