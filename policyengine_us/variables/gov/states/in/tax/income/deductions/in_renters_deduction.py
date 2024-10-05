from policyengine_us.model_api import *


class in_renters_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana renter's deduction"
    unit = USD
    definition_period = YEAR
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2-6"
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["in"].tax.income
        filing_status = tax_unit("filing_status", period)
        max_deduction = p.deductions.renters.max[filing_status]
        rent_paid = add(tax_unit, period, ["rent"])
        return min_(rent_paid, max_deduction)
