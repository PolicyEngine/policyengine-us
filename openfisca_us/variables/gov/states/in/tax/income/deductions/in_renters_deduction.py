from openfisca_us.model_api import *


class in_renters_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN Renter's deductions"
    unit = USD
    definition_period = YEAR
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2-6"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["in"].tax.income.deductions
        filing_status = tax_unit("filing_status", period)
        max_renters_deduction = p.renters.max[filing_status]
        in_rent = tax_unit("in_rent", period)
        return min(in_rent, max_renters_deduction)
