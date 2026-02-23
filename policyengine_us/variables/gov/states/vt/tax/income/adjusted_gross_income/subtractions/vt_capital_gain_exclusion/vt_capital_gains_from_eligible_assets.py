from policyengine_us.model_api import *


class vt_capital_gains_from_eligible_assets(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont capital gains from assets eligible for 40% exclusion"
    unit = USD
    documentation = (
        "Net capital gains from assets eligible for Vermont's 40% "
        "capital gains percentage exclusion. Eligible assets must be "
        "held for 3+ years and exclude stocks and bonds publicly "
        "traded on established securities markets, financial "
        "instruments, depreciable personal property (except farm "
        "property and standing timber), and real estate used as a "
        "residence. Defaults to 0, meaning only the flat $5,000 "
        "exclusion applies."
    )
    definition_period = YEAR
    defined_for = StateCode.VT
    default_value = 0
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-153-2024.pdf#page=2",
        "https://legislature.vermont.gov/statutes/section/32/151/05811",
    )
