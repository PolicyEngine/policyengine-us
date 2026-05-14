from policyengine_us.model_api import *


class sstb_self_employment_income_before_lsr(Variable):
    value_type = float
    entity = Person
    label = "SSTB self-employment income before labor supply responses"
    unit = USD
    documentation = (
        "SSTB self-employment non-farm income before labor supply responses."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/1402#a",
        "https://www.law.cornell.edu/uscode/text/26/199A#d_2",
    )
    uprating = "calibration.gov.irs.soi.self_employment_income"
