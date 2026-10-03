from policyengine_us.model_api import *


class investment_income_form_4952(Variable):
    value_type = float
    entity = TaxUnit
    label = "Investment income from Form 4952"
    documentation = (
        "The federal Form 4952 amount that California form FTB 3526 line 9 "
        "asks for (federal Form 4952 line 8). The federal Schedule D Tax "
        "Worksheet does not read this input; it takes the Form 4952 line 4g "
        "election from investment_income_elected_form_4952."
    )
    unit = USD
    definition_period = YEAR
    reference = dict(
        title="2021 California form FTB 3526, line 9",
        href="https://www.ftb.ca.gov/forms/2021/2021-3526.pdf",
    )
