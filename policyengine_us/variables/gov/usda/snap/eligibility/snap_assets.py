from policyengine_us.model_api import *


class snap_assets(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = (
        "Countable liquid assets for SNAP resource limits. "
        "Includes bank accounts, stocks, and bonds per "
        "7 USC 2014(g). Excludes retirement accounts, "
        "education savings, and vehicles."
    )
    label = "SNAP assets"
    unit = USD
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2014#g",
    )

    adds = ["spm_unit_cash_assets"]
