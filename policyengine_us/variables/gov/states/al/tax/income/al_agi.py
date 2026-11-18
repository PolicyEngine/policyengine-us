from policyengine_us.model_api import *


class al_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama adjusted gross income"
    documentation = (
        "Alabama adjusted gross income of the head and spouse. A tax unit "
        "dependent's income and deductions belong on the dependent's own "
        "Alabama return, so they are left out."
    )
    defined_for = StateCode.AL
    unit = USD
    definition_period = YEAR
    reference = (
        "https://alison.legislature.state.al.us/code-of-alabama?section=40-18-14",
        # Every resident individual is taxed on their own income, and every
        # taxpayer over the filing threshold files their own return.
        "https://alison.legislature.state.al.us/code-of-alabama?section=40-18-2",
        "https://alison.legislature.state.al.us/code-of-alabama?section=40-18-27",
        # Ala. Admin. Code r. 810-3-27-.01(1): only a husband and wife may
        # combine their income on one return.
        "https://admincode.legislature.state.al.us/administrative-code/810-3-27",
        # Dependents who meet the filing requirements file their own return.
        "https://www.revenue.alabama.gov/wp-content/uploads/2026/01/25f40bk.pdf#page=5",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.al.tax.income.agi
        gross_income = tax_unit_non_dep_add(tax_unit, period, p.gross_income_sources)
        deductions = tax_unit_non_dep_add(tax_unit, period, p.deductions)
        return gross_income - deductions
