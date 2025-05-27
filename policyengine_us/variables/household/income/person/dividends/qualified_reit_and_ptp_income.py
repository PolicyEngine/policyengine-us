from policyengine_us.model_api import *


class qualified_reit_and_ptp_income(Variable):
    value_type = float
    entity = Person
    label = "REIT and PTP Income"
    unit = USD
    documentation = "REIT and Publically Traded Partnership Income. Part of the QBID calclulation."
    definition_period = YEAR
    # Uprate using the same series as other dividend income.
    uprating = "calibration.gov.irs.soi.qualified_dividend_income"
