from policyengine_us.model_api import *


class long_term_capital_gains_on_assets_eligible_for_vt_exclusion(Variable):
    value_type = float
    entity = Person
    label = "Long-term capital gains on assets eligible for Vermont's 40% exclusion"
    unit = USD
    documentation = (
        "Vermont's 40% capital gains exclusion only applies to gains from qualifying "
        "assets held more than 3 years, excluding: stocks and bonds publicly traded or "
        "traded on an exchange, any other financial instruments, depreciable personal "
        "property (other than farm property and standing timber), and real estate. "
        "Qualifying assets typically include: farms, businesses, and certain timber."
    )
    definition_period = YEAR
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-153-2024.pdf#page=2",
        "https://legislature.vermont.gov/statutes/section/32/151/05811",
    )
