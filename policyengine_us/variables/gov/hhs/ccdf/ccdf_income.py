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
        "workers' compensation, and Social Security. Federal law does not "
        "define which sources count — 45 CFR 98.16(a)(1) leaves the "
        "definition of income to each state's CCDF plan — so this is a "
        "cross-state approximation. States that enumerate their own sources "
        "define a state countable-income variable instead, as New York does "
        "in ny_ccap_countable_income and Ohio in oh_ccap_countable_income. "
        "State CCDF programs may also define a different assistance unit. "
        "TANF and other public assistance are countable under most state "
        "plans but are omitted here because counting them creates a "
        "CCDF-to-TANF circular dependency through the TANF dependent care "
        "deduction (see in_ccdf_gross_income and "
        "gov/states/in/fssa/ccdf/income/sources.yaml). This measure also "
        "over-includes relative to some state plans — capital gains, illicit "
        "income, general assistance and miscellaneous income all flow in "
        "through market_income and its components."
    )
    reference = "https://www.ecfr.gov/current/title-45/section-98.16#p-98.16(a)(1)"
    adds = [
        "market_income",
        # market_income covers only non-government sources, so government
        # income streams follow separately.
        "child_support_received",
        "unemployment_compensation",
        "workers_compensation",
        # social_security includes the dependents, disability, retirement,
        # and survivors components. It is OASDI only and excludes SSI.
        "social_security",
    ]
