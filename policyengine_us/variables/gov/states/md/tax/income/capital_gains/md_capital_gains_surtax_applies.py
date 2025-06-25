from policyengine_us.model_api import *


class md_capital_gains_surtax_applies(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Maryland capital gains surtax applies"
    definition_period = YEAR
    reference = [
        "https://mgaleg.maryland.gov/2025RS/bills/hb/hb0352E.pdf#page=159"  # Maryland House Bill 352 - Budget Reconciliation and Financing Act of 2025
    ]
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.md.tax.income.capital_gains

        # Check federal AGI threshold
        federal_agi = tax_unit("adjusted_gross_income", period)

        return federal_agi > p.surtax_threshold
