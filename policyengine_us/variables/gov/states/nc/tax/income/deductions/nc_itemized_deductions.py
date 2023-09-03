from policyengine_us.model_api import *


class nc_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina itemized deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.ncdor.gov/taxes-forms/individual-income-tax/north-carolina-standard-deduction-or-north-carolina-itemized-deductions "
    defined_for = StateCode.NC

    def formula(tax_unit, period, parameters):
        # Qualified Mortgage Interest and Real Estate Property Taxes.
        p = parameters(period).gov.states.nc.tax.income.deductions.itemized.cap
        filing_status = tax_unit("filing_status", period)

        mortgage_interest = add(tax_unit, period, ["mortgage_interest"])

        property_taxes = min_(
            add(tax_unit, period, ["real_estate_taxes"]),
            p.real_estate[filing_status],
        )

        capped_mortage_and_property_taxes = min_(
            mortgage_interest + property_taxes, p.mortgage_and_property_tax
        )

        # North Carolina specifies a state and local tax deduction cap which is currently not modeled in PolicyEngine

        charitable_deduction = tax_unit("charitable_deduction", period)

        # Medical and Dental Expenses.
        medical = tax_unit("medical_expense_deduction", period)

        return (
            capped_mortage_and_property_taxes + medical + charitable_deduction
        )
