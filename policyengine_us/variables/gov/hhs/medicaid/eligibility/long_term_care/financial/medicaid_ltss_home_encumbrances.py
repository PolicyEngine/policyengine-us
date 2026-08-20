from policyengine_us.model_api import *


class medicaid_ltss_home_encumbrances(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS home encumbrances"
    unit = USD
    quantity_type = STOCK
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Explicit current enforceable debt secured by the home and deducted "
        "from market value before applying the applicant's ownership share "
        "in the Medicaid LTSS home-equity payment-bar calculation."
    )
    reference = "https://www.law.cornell.edu/uscode/text/42/1396p#f"
