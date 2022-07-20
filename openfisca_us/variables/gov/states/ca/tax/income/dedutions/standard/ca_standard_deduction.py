from openfisca_us.model_api import *


class ca_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "California Standard Deduction"
    unit = USD
    documentation = "https://www.ftb.ca.gov/forms/2021/2021-540.pdf"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.deductions.standard
        filing_status = tax_unit("filing_status", period)
        amount_if_eligible = p.amount[filing_status]
        in_ca = tax_unit.household("state_code_str", period) == "CA"
        eligible = in_ca
        return eligible * amount_if_eligible
