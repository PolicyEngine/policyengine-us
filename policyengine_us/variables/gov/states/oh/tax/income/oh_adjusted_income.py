from policyengine_us.model_api import *


class oh_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "OH adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        ""
    )
    defined_for = StateCode.OH

    adds = ["investment_in_529_plan",
            "oh_bonus_depreciation_add_back",
            "oh_other_add_backs"]
    
    subtracts = ["oh_section_179_expense_add_back", 
                 "qualified_business_income_deduction",
                 "tax_unit_taxable_social_security",
                 "dividend_income",
                 ]
