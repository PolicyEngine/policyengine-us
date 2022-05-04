from openfisca_us.model_api import *


class self_employment_tax_ald(Variable):
    value_type = float
    entity = TaxUnit
    label = "Self-employment tax ALD deduction"
    unit = USD
    documentation = "Above-the-line deduction for self-employment tax"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/164#f"

    def formula(tax_unit, period, parameters):
        self_employment_tax = add(tax_unit, period, ["self_employment_tax"])
        percent_deductible = parameters(
            period
        ).irs.ald.self_employment_tax.percent_deductible
        return self_employment_tax * percent_deductible
