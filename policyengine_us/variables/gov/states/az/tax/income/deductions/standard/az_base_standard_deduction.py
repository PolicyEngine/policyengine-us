from policyengine_us.model_api import *


class az_base_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona base standard deduction"
    unit = USD
    documentation = "https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01041.htm"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        # Arizona standard deduction follows federal standard deduction
        p = parameters(period).gov.irs.deductions.standard
        filing_status = tax_unit("az_filing_status", period)
        return p.amount[filing_status]
