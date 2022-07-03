from openfisca_us.model_api import *


class va_age_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "VA age deduction"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        gov = parameters(period).gov
        va_deductions_path = (
            gov.states.va.tax.deductions.income_based_age_deduction
        )
        age_thd = va_deductions_path.age
        # number of tax payers claiming an income based deduction
        filing_status = tax_unit("filing_status", period)
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)

        n_filers = (age_head >= age_thd) + (age_spouse >= age_thd)
        if n_filers == 0:
            return 0

        agi = tax_unit("adjusted_gross_income", period)

        fdc_addition = 0  # fixed date conformity addition. need to add later
        fdc_subtraction = 0  # FDC subtraction. add later
        agi_fdc = agi + fdc_addition - fdc_subtraction

        ss_railroad_ben = 0  # social security and railroad retirement bennies
        afagi = agi_fdc - ss_railroad_ben
        agi_threshold = va_deductions_path["income"][filing_status]
        if afagi < agi_threshold:
            return va_deductions_path["deduction"] * n_filers
        else:
            diff = afagi - agi_threshold
            max_amt = va_deductions_path["deduction"] * n_filers
            return max(max_amt - diff, 0)
