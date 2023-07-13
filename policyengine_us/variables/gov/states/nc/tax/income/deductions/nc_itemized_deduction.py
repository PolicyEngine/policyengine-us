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
        p = parameters(period).gov.states.nc.tax.income.deductions.itemized
        filing_status = tax_unit("filing_status", period)

        mortgage_deduction = min_(
            p.mortgage_limit, add(tax_unit, period, ["mortgage_interest"])
        )

        property_taxes = min_(
            p.property_taxes_limit[filing_status],
            add(tax_unit, period, ["property_tax_primary_residence"]),
        )

        salt = tax_unit("state_and_local_sales_or_income_tax", period)

        mortgage_interest_and_real_estate_property_taxes = min_(
            p.mortgage_and_property_taxes_limit,
            (mortgage_deduction + property_taxes + salt),
        )

        #  If the amount of the home mortgage interest and real estate taxes paid by both spouses exceeds $20,000,
        #  these deductions must be prorated based on the percentage paid by each spouse.

        # Medical and Dental Expenses.
        medical = tax_unit("medical_expense_deduction", period)

        # Charitable Contributions.

        charitable = tax_unit("charitable_deduction", period)

        return (
            mortgage_interest_and_real_estate_property_taxes
            + medical
            + charitable
        )
