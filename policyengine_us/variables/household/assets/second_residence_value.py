from policyengine_us.model_api import *


class second_residence_value(Variable):
    value_type = float
    entity = Person
    label = "Second residence value"
    documentation = (
        "Market value of the person's share of their second residence, not "
        "assessed value: the one home besides the main home that the taxpayer "
        "treats as a qualified residence for mortgage interest, such as a "
        "vacation home. Under the pre-TCJA mortgage interest limits, which New "
        "York keeps, home equity debt on this home can't exceed its value, the "
        "sum of these shares in the tax unit, less the part of "
        "second_home_mortgage_balance treated as acquisition debt. "
        "primary_residence_value plays the same part for the main home. "
        "Publication 936 (2017) measures the value and that debt on "
        "the date the last debt was secured by the home; PolicyEngine "
        "approximates both with this value and the current balances. Leave at "
        "0 if unknown: PolicyEngine then counts the home as worth at least the "
        "debt on it."
    )
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
    reference = (
        # 26 U.S.C. 163(h)(3)(C)(i) and (h)(4)(A), 2016 edition.
        "https://www.govinfo.gov/content/pkg/USCODE-2016-title26/html/USCODE-2016-title26-subtitleA-chap1-subchapB-partVI-sec163.htm",
        # PDF pages 10, 13
        "https://www.irs.gov/pub/irs-prior/p936--2017.pdf#page=10",
    )
