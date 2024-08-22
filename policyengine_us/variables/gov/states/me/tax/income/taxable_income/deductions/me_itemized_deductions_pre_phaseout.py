from policyengine_us.model_api import *


class me_itemized_deductions_pre_phaseout(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine itemized deductions before phaseout"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_2_ff.pdf",
        "https://www.mainelegislature.org/legis/statutes/36/title36sec5125.html",
    )
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        # Whether or not the taxpayer itemized for federal taxes.
        us_itemizing = tax_unit("tax_unit_itemizes", period)

        # Get the Maine itemizing deduction parameters.
        p = parameters(period).gov.states.me.tax.income.deductions.itemized

        # Get federal itemized deductions minus SALT (Section 3A).
        deduction = tax_unit("itemized_deductions_less_salt", period)

        # Get medical (and dental) expenses.
        medical_expenses = tax_unit("medical_expense_deduction", period)

        # Get real estate (and property) taxes.
        real_estate_taxes = add(tax_unit, period, ["real_estate_taxes"])

        # Calculate uncapped (potential) itemized deductions.
        deduction_no_med = deduction - medical_expenses + real_estate_taxes

        # Calculate capped itemized deductions.
        capped_deduction_no_med = min_(deduction_no_med, p.cap)

        # Add back medical and dental expenses (which are not capped).
        return us_itemizing * (capped_deduction_no_med + medical_expenses)
