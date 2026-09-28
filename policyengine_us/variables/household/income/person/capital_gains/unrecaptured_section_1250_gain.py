from policyengine_us.model_api import *


class unrecaptured_section_1250_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "Un-recaptured section 1250 gain"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.long_term_capital_gains"
    reference = dict(
        title="26 U.S. Code § 1250(a)",
        href="https://www.law.cornell.edu/uscode/text/26/1250#a",
    )
