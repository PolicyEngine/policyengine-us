from policyengine_us.model_api import *


class non_sch_d_capital_gains(Variable):
    value_type = float
    entity = Person
    label = "Capital gains not reported on Schedule D"
    unit = USD
    documentation = (
        "Capital gain distributions (Form 1099-DIV box 2a) reported on Form "
        "1040 line 7a without Schedule D. A filer who also has capital losses "
        "or other capital gains enters them on Schedule D line 13, so the "
        "model nets them with those gains and losses before the capital loss "
        "limit (loss_limited_net_capital_gains, "
        "capital_losses_allowed_against_gains and limited_capital_loss)."
    )
    reference = dict(
        title="2025 Instructions for Schedule D (Form 1040), Capital Gain Distributions",
        href="https://www.irs.gov/pub/irs-prior/i1040sd--2025.pdf#page=2",
    )
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.long_term_capital_gains"
