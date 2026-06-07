from policyengine_us.model_api import *


class mt_federal_obbba_subtraction(Variable):
    value_type = float
    entity = Person
    label = "Montana subtraction for federal OBBBA Schedule 1-A deductions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0200/0150-0300-0210-0200.html",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2025_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=7",
        "https://www.congress.gov/119/bills/hr1/BILLS-119hr1enr.pdf#page=88",
        "https://www.congress.gov/119/bills/hr1/BILLS-119hr1enr.pdf#page=96",
    )

    def formula(person, period, parameters):
        is_head = person("is_tax_unit_head", period)
        senior = person.tax_unit("additional_senior_deduction", period)
        tips = person.tax_unit("tip_income_deduction", period)
        overtime = person.tax_unit("overtime_income_deduction", period)
        auto = person.tax_unit("auto_loan_interest_deduction", period)
        return is_head * (senior + tips + overtime + auto)
