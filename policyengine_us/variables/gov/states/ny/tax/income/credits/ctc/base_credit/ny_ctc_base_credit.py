from policyengine_us.model_api import *


class ny_ctc_base_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "The base NY CTC credit before reduction"
    documentation = "New York's Empire State Child Credit Worksheet A / B Part 2"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.ny.gov/pdf/2021/inc/it213i_2021.pdf"
    defined_for = StateCode.NY


    def formula(tax_unit, period, parameters):
        income_tax = tax_unit("income_tax", period)
        # Line 19 and 19a from Form IT-201 - these are the same in our model
        selected_credit_amount = tax_unit("ny_ctc_federal_credits", period)
        # If the filer claimed additional credit, the base credit is reduced by the amount of the selected credits
        # We currently skip this caluclation as we only compute the residential energy credit
        reduced_tax = max_(0, income_tax - selected_credit_amount)
        pre_reduction_base_credit = tax_unit("ny_ctc_pre_reduction_base_credit", period)
        base_credit_over_reduced_tax = pre_reduction_base_credit > reduced_tax
        return where(base_credit_over_reduced_tax, reduced_tax, pre_reduction_base_credit)
