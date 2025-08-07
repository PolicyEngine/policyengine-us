from policyengine_us.model_api import *


class ia_regular_tax_consolidated(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa regular tax for years on or after 2023"
    unit = USD
    definition_period = YEAR
    reference = "https://revenue.iowa.gov/media/2748/download?inline"
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("ia_taxable_income_consolidated", period)
        p = parameters(period).gov.states.ia.tax.income.rates
        filing_status = tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        return where(
            joint,
            p.by_filing_status.joint.calc(taxable_income),
            p.by_filing_status.other.calc(taxable_income),
        )
