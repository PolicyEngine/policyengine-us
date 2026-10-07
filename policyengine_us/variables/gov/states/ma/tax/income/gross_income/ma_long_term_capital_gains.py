from policyengine_us.model_api import *


class ma_long_term_capital_gains(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA long-term capital gains and losses"
    documentation = (
        "Long-term amounts on Massachusetts Schedule D: long-term capital "
        "gains and losses, capital gain distributions reported without a "
        "federal Schedule D (line 6) and Form 4797, Part II gains and losses "
        "(line 7). PolicyEngine has a single Form 4797 input, so it also "
        "counts any gain or loss on business property held one year or less, "
        "which belongs on Schedule B, lines 12 and 17."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://taxsim.nber.org/historical_state_tax_forms/MA/2023/dor-2023-inc-sch-d-(form-1).pdf",
        "https://taxsim.nber.org/historical_state_tax_forms/MA/2023/dor-2023-inc-form1-instructions.pdf#page=27",
    )
    defined_for = StateCode.MA
    adds = [
        "long_term_capital_gains",
        "non_sch_d_capital_gains",
        "other_net_gain",
    ]
