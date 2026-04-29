from policyengine_us.model_api import *


class sstb_self_employment_income(Variable):
    value_type = float
    entity = Person
    label = "SSTB self-employment income"
    unit = USD
    documentation = (
        "Self-employment non-farm income from a specified service trade or "
        "business (SSTB) under IRC §199A(d)(2). Subject to SECA tax. For the "
        "qualified business income deduction, this income is treated separately "
        "from non-SSTB self-employment income because the SSTB applicable "
        "percentage phaseout above the threshold can fully eliminate the "
        "deduction without affecting non-SSTB QBI."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/1402#a",
        "https://www.law.cornell.edu/uscode/text/26/199A#d_2",
    )
    adds = [
        "sstb_self_employment_income_before_lsr",
        "sstb_self_employment_income_behavioral_response",
    ]
    uprating = "calibration.gov.irs.soi.self_employment_income"
