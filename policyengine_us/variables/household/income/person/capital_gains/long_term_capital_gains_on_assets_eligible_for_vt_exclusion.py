from policyengine_us.model_api import *


class long_term_capital_gains_on_assets_eligible_for_vt_exclusion(Variable):
    value_type = float
    entity = Person
    label = "Long-term capital gains on assets eligible for Vermont's 40% exclusion"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VT
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-153-2024.pdf#page=2",
        "https://legislature.vermont.gov/statutes/section/32/151/05811",
    )
