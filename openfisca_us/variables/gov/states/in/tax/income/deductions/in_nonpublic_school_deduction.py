from openfisca_us.model_api import *


class in_nonpublic_school_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Nonpublic school expenditures deduction for IN"
    definition_period = YEAR
    unit = USD
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2-4"  # (d)(1)

    def formula(tax_unit, period, parameters):
        p = (
            parameters(period)
            .gov.states["in"]
            .tax.income.deductions.nonpublic_school
        )
        return (
            tax_unit("in_count_children_nonpublic_school", period) * p.amount
        )
