from policyengine_us.model_api import *


class snap_assets(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = (
        "Countable liquid resources for SNAP asset limits. "
        "Per 7 CFR 273.8(c)(1), liquid resources include "
        "cash on hand, checking and savings accounts, "
        "stocks, and bonds. Excluded per 7 USC 2014(g)(2-5): "
        "home, retirement accounts (401k/IRA), "
        "education savings (529/Coverdell), and vehicles "
        "(subject to state fair-market-value exemptions)."
    )
    label = "SNAP assets"
    unit = USD
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2014#g",
        "https://www.law.cornell.edu/cfr/text/7/273.8",
    )

    # Liquid resources per 7 CFR 273.8(c)(1):
    # bank_account_assets = checking, savings, money market
    #                       (SIPP TVAL_BANK)
    # stock_assets = stocks and mutual funds (SIPP TVAL_STMF)
    # bond_assets = bonds and government securities
    #               (SIPP TVAL_BOND)
    adds = ["bank_account_assets", "stock_assets", "bond_assets"]
