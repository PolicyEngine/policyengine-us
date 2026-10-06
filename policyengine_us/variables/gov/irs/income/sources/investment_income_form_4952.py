from policyengine_us.model_api import *


class investment_income_form_4952(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal Form 4952 line 8 amount for California FTB 3526"
    documentation = (
        "The federal Form 4952 amount that California form FTB 3526 line 9 "
        "asks for (federal Form 4952 line 8). Defaults to the model's federal "
        "investment_interest_expense_deduction; an input overrides it, for "
        "example a federal deduction that includes amounts the model does "
        "not compute. The federal Schedule D Tax Worksheet does not read "
        "this variable; it takes the Form 4952 line 4g election from "
        "form_4952_elected_investment_income."
    )
    unit = USD
    definition_period = YEAR
    reference = dict(
        title="2021 California form FTB 3526, line 9",
        href="https://www.ftb.ca.gov/forms/2021/2021-3526.pdf",
    )

    def formula(tax_unit, period, parameters):
        return tax_unit("investment_interest_expense_deduction", period)
