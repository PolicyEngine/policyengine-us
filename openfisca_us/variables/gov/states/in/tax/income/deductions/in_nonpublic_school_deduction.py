from openfisca_us.model_api import *


class in_nonpublic_school_deduction(Variable):
    value_type = float
    entity = Person
    label = "Nonpublic school expenditures deduction for IN"
    definition_period = YEAR
    unit = currency - USD
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2-4"  # (d)(1)

    def formula(tax_unit, period, parameters):
        amount = (
            parameters(period)
            .gov.states["in"]
            .tax.income.deductions.nonpublic_school.amount
        )
        return tax_unit("in_num_children_nonpublic_school", period) * amount
