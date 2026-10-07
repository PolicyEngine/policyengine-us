from policyengine_us.model_api import *


class ky_itemized_deductions_unit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.ky.gov/Forms/Form%20740%20Schedule%20A%202022.pdf",
        "https://law.justia.com/codes/kentucky/2022/chapter-141/section-141-019/",  # (2)(i)
        "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=57914#page=4",  # (2)(j)
    )
    defined_for = StateCode.KY

    adds = ["itemized_deductions_less_salt"]
    subtracts = [
        "medical_expense_deduction",
        "ky_disallowed_second_residence_interest",
    ]
