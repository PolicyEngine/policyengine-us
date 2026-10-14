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
        # 2019 Ky. Acts ch. 151, sec. 37: wagering losses allowed from 2019
        # PDF pages 60, 112
        "https://apps.legislature.ky.gov/law/acts/19RS/documents/0151.pdf#page=60",
    )
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ky.tax.income.deductions.itemized
        deductions = tax_unit("itemized_deductions_less_salt", period) - tax_unit(
            "medical_expense_deduction", period
        )
        if p.wagering_losses_allowed:
            return deductions
        # KRS 141.019(2) excluded every section 165 loss for 2018.
        return deductions - tax_unit("wagering_losses_deduction", period)
