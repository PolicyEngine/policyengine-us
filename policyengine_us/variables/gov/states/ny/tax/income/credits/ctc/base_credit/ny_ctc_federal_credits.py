from policyengine_us.model_api import *


class ny_ctc_federal_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY Worksheet A/B for Form IT-213 federal credit computation"
    documentation = "New York's Empire State Child Credit Worksheet A and B"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.ny.gov/pdf/2021/inc/it213i_2021.pdf#page=2"
    defined_for = StateCode.NY

    # Line 8 of Worksheet A, Line 10 of worksheet B
    adds = [
        # a: Form 1040, Schedule 3, line 1, Foreign tax credit
        "foreign_tax_credit",
        # b: Form 1040, Schedule 3, line 2, Credit for child and dependent care expenses
        "cdcc",
        # c Form 1040, Schedule 3, line 3, Education credits
        "education_tax_credits",
        # d Form 1040, Schedule 3, line 4, Retirement savings contributions credit
        "savers_credit",
        # e Form 1040, Schedule 3, line 6l, Total increase/decrease to reporting year tax
        # f Form 8910, Alternative Motor Vehicle Credit
        # g Form 8936, Qualified Plug-in Electric Drive Motor Vehicle Credit, line 23
        # h Schedule R, Credit for the Elderly or the Disabled, line 22
        "elderly_disabled_credit",
    ]
