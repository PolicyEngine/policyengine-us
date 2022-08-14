from openfisca_us.model_api import *


class in_renters_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN renter's deductions"
    unit = USD
    definition_period = YEAR
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2-6"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["in"].tax.income.deductions
        filing_status = tax_unit("filing_status", period)
        max_renters_deduction = p.renters.max[filing_status]
        in_rent = add(tax_unit, period, ["rent"])
        # using national rent var to save mem but law specifices only IN rent allowed
        return min_(in_rent, max_renters_deduction)
