from policyengine_us.model_api import *


class ccdf_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "CCDF income approximation"
    definition_period = YEAR
    unit = USD
    documentation = (
        "Approximates CCDF countable income as market income plus government "
        "income streams: child support received, unemployment compensation, "
        "workers' compensation, and Social Security. State CCDF programs may "
        "define a different assistance unit and count different income "
        "sources. TANF and other public assistance are countable under most "
        "state plans but are omitted here because counting them creates a "
        "CCDF-to-TANF circular dependency through the TANF dependent care "
        "deduction (see in_ccdf_gross_income and "
        "gov/states/in/fssa/ccdf/income/sources.yaml)."
    )
    reference = "https://www.law.cornell.edu/uscode/text/42/9858n#4_B"
    adds = [
        "market_income",
        # market_income covers only non-government sources, so government
        # income streams follow separately.
        "child_support_received",
        "unemployment_compensation",
        "workers_compensation",
        # social_security includes the dependents, disability, retirement,
        # and survivors components.
        "social_security",
    ]
