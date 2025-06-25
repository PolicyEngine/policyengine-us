from policyengine_us.model_api import *


class md_capital_gains_surtax_applies(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Maryland capital gains surtax applies"
    definition_period = YEAR
    reference = [
        "https://mgaleg.maryland.gov/2025RS/Chapters_noln/CH_604_hb0352e.pdf#page=160"  # Maryland House Bill 352 - Budget Reconciliation and Financing Act of 2025
    ]
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.md.tax.income.capital_gains

        # Check Maryland AGI threshold
        md_agi = tax_unit("md_agi", period)

        return md_agi > p.surtax_threshold
