from policyengine_us.model_api import *


class de_wilmington_earned_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wilmington earned income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE
    reference = (
        "https://wilmdebudget.org/wp-content/uploads/2024/03/fy25-tax-rates.pdf#page=1"
    )

    def formula(tax_unit, period, parameters):
        rate = parameters(period).gov.local.de.wilmington.tax.income.rate
        person = tax_unit.members
        # Residents are taxed on all earned income; nonresidents on their
        # Wilmington-source earnings (provided as an input).
        resident = tax_unit.household("in_wilmington", period)
        earnings = max_(
            person("employment_income", period)
            + person("self_employment_income", period),
            0,
        )
        resident_tax = where(resident, tax_unit.sum(earnings), 0) * rate
        nonresident_earnings = person("de_wilmington_nonresident_earnings", period)
        nonresident_tax = tax_unit.sum(max_(nonresident_earnings, 0)) * rate
        return resident_tax + where(resident, 0, nonresident_tax)
