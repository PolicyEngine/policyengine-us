from policyengine_us.model_api import *


class in_add_backs(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana add-backs"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5",
        # Information Bulletin 119: IC 6-3-1-3.5(a)(26) adds back the 2020
        # IRC 62(a)(22) charitable deduction (code 120).
        "https://www.in.gov/dor/files/reference/ib119.pdf#page=2",
    )
    defined_for = StateCode.IN

    adds = [
        "charitable_contributions_ald",
        "in_bonus_depreciation_add_back",
        "in_nol_add_back",
        "in_oos_municipal_obligation_interest_add_back",
        "in_other_additions",
        "in_section_179_expense_add_back",
        "in_tax_add_back",
    ]
