from policyengine_us.model_api import *


class unrecaptured_section_1250_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "Un-recaptured section 1250 gain"
    unit = USD
    documentation = (
        "Unrecaptured section 1250 gain as reported on Schedule D line 19: "
        "already reduced by the losses the 28-percent rate gain does not "
        "absorb (line 17 of the Unrecaptured Section 1250 Gain Worksheet), "
        "so the model does not reduce it again. The microdata carry it from "
        "the PUF's Schedule D line 19. Enter the gain before those losses as "
        "unrecaptured_section_1250_gain_before_losses instead. Memo item: "
        "long_term_capital_gains already includes it."
    )
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.long_term_capital_gains"
    reference = [
        dict(
            title="26 U.S. Code § 1(h)(6)(A)",
            href="https://www.law.cornell.edu/uscode/text/26/1#h_6_A",
        ),
        dict(
            title="2025 Instructions for Schedule D (Form 1040), Unrecaptured Section 1250 Gain Worksheet—Line 19",
            href="https://www.irs.gov/pub/irs-prior/i1040sd--2025.pdf#page=13",
        ),
    ]
