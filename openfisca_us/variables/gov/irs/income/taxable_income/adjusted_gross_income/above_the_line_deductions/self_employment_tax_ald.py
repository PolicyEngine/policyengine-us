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
        person = tax_unit.members
        self_employment_tax = person("self_employment_tax", period)
        is_dependent = person("is_tax_unit_dependent", period)
        total_tax = tax_unit.sum(self_employment_tax * ~is_dependent)
        percent_deductible = parameters(
            period
        ).irs.ald.self_employment_tax.percent_deductible
        return total_tax * percent_deductible
