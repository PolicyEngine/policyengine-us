from policyengine_us.model_api import *


class ne_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "NE standard deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdf"
        "https://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf"
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        base_state_sd = tax_unit("ne_base_standard_deduction", period)
        base_fed_sd = tax_unit("basic_standard_deduction", period)
        smaller_base_sd = min_(base_state_sd, base_fed_sd)
        additional_sd = tax_unit("additional_standard_deduction", period)
        return smaller_base_sd + additional_sd
