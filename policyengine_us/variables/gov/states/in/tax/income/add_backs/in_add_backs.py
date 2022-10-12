from policyengine_us.model_api import *


class in_add_backs(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN add-backs"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5"
    )

    formula = sum_of_variables(
        [
            "in_bonus_depreciation_add_back",
            "in_nol_add_back",
            "in_oos_municipal_obligation_interest_add_back",
            "in_other_add_backs",
            "in_section_179_expense_add_back",
            "in_tax_add_back",
        ]
    )
