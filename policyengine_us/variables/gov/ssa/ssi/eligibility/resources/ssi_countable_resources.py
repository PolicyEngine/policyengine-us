from policyengine_us.model_api import *


class ssi_countable_resources(Variable):
    value_type = float
    entity = Person
    label = "SSI countable resources"
    documentation = (
        "Countable resources for SSI eligibility. Includes liquid assets "
        "(bank accounts, stocks, bonds) but excludes home, one vehicle, "
        "household goods, and retirement accounts per SSI rules."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ssa.gov/ssi/spotlights/spot-resources.htm",
        "https://www.law.cornell.edu/uscode/text/42/1382b",
    )

    def formula(person, period, parameters):
        # SSI counts liquid assets but excludes:
        # - Home and land
        # - One vehicle (with exceptions)
        # - Household goods and personal effects
        # - Burial plots and up to $1,500 in burial funds
        # - Life insurance with face value <= $1,500
        # - Retirement accounts (excluded under ABLE Act for some)
        #
        # Current imputation includes:
        # - Bank accounts (checking, savings, money market)
        # - Stocks and mutual funds
        # - Bonds and government securities
        bank = person("bank_account_assets", period)
        stocks = person("stock_assets", period)
        bonds = person("bond_assets", period)
        return bank + stocks + bonds
