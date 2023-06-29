from policyengine_us.model_api import *

class nc_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina itemized deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ncdor.gov/taxes-forms/individual-income-tax/north-carolina-standard-deduction-or-north-carolina-itemized-deductions "
    )
    defined_for = StateCode.nc

    def formula(tax_unit, period, parameters):
        
        # Qualified Mortgage Interest and Real Estate Property Taxes.
        p = parameters(period).gov.states.nc.tax.income.deductions.itemized
        filing_status = tax_unit("filing_status", period)

        mortgage_deduction = min_(p.mortgage_limit,
        add(tax_unit, period, ["mortgage_taxes"]))
        
        property_taxes = min_(p.property_taxes_limit[filing_status],
        add(tax_unit, period, ["property_tax_primary_residence"]))

        salt = tax_unit("state_and_local_sales_or_income_tax", period)

        mortgage_interest_and_real_estate_property_taxes  = min_(20000, add(mortgage_deduction,property_taxes,salt))

        #  If the amount of the home mortgage interest and real estate taxes paid by both spouses exceeds $20,000, 
        #  these deductions must be prorated based on the percentage paid by each spouse.

        # Medical and Dental Expenses.
        nc_p = parameters(period).gov.states.nc.tax.income.agi.subtractions
        max_decoupled_year_offset = nc_p.max_care_expense_year_offset
        period_max = period.offset(max_decoupled_year_offset)
        nc_max_care_expense = parameters(period_max).gov.irs.credits.cdcc.max
        max_eligibles = parameters(period).gov.irs.credits.cdcc.eligibility.max
        num_eligibles = min_(
            max_eligibles, tax_unit("count_cdcc_eligible", period)
        )
        us_expenses = tax_unit("cdcc_relevant_expenses", period)
        medical = min_(md_max_care_expense * num_eligibles, us_expenses)

        # Charitable Contributions.

        charitable = tax_unit("charitable_deduction", period)

        return itemized_deductions

