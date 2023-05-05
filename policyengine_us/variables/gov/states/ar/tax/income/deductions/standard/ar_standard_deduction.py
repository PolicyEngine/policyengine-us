from policyengine_us.model_api import *


class ar_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas standard deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=14"
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ar.tax.income.deductions
        filing_status = tax_unit("filing_status", period)
        return p.standard[filing_status]
