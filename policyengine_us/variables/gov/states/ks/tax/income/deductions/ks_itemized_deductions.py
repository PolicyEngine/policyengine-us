from policyengine_us.model_api import *


class ks_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevisor.gov/statutes/chapters/ch79/079_032_0120.html",
        "https://www.ksrevenue.gov/pdf/ip17.pdf#page=14",
        "https://www.ksrevenue.gov/pdf/ip25.pdf#page=14",
    )
    defined_for = StateCode.KS

    def formula(tax_unit, period, parameters):
        # K.S.A. 79-32,120(a) limits the Kansas itemized deduction to four
        # federal categories, each at a year-specific share. Other federal
        # itemized deductions (investment interest, casualty and theft losses,
        # miscellaneous deductions) do not count. Property taxes are not limited
        # by the federal cap on state and local taxes.
        p = parameters(period).gov.states.ks.tax.income.deductions.itemized.rate
        charitable = tax_unit("charitable_deduction", period)
        medical = tax_unit("medical_expense_deduction", period)
        qualified_residence_interest = tax_unit(
            "deductible_mortgage_interest_tax_unit", period
        )
        property_taxes = add(tax_unit, period, ["real_estate_taxes"])
        return (
            p.charitable_contributions * charitable
            + p.medical_expenses * medical
            + p.qualified_residence_interest * qualified_residence_interest
            + p.property_taxes * property_taxes
        )
