from policyengine_us.model_api import *


class medicaid_ltss_home_equity_hardship_waiver(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid LTSS home-equity hardship waiver"
    definition_period = MONTH
    default_value = False
    documentation = (
        "Trusted indication that the administering agency has granted an "
        "undue-hardship waiver of the Medicaid LTSS home-equity payment bar. "
        "The model does not apply hardship criteria or adjudicate the waiver."
    )
    reference = "https://www.law.cornell.edu/uscode/text/42/1396p#f_4"
