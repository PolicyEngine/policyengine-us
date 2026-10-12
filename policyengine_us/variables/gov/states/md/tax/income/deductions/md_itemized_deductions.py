from policyengine_us.model_api import *


class md_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = [
        "https://mgaleg.maryland.gov/2022RS/Statute_Web/gtg/10-218.pdf#page=1",
        "https://interactive.marylandtaxes.gov/Individuals/iFile_ChooseForm/PriorYearForms/Resident_Booklet_2021.pdf#page=5",
        "https://interactive.marylandtaxes.gov/Individuals/iFile_ChooseForm/PriorYearForms/Resident_Booklet_2022.pdf#page=5",
        "https://mgaleg.maryland.gov/2025RS/Chapters_noln/CH_604_hb0352e.pdf#page=167",  # Maryland House Bill 352 - Budget Reconciliation and Financing Act of 2025
    ]
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        # Base itemized deductions (federal itemized deductions less SALT plus capped property taxes)
        base_itemized = add(
            tax_unit,
            period,
            ["itemized_deductions_less_salt", "capped_property_taxes"],
        )

        # Apply income-based phase-out if applicable
        p = parameters(period).gov.states.md.tax.income.deductions.itemized
        if p.phase_out.applies:
            filing_status = tax_unit("filing_status", period)
            md_agi = tax_unit("adjusted_gross_income", period)

            # Calculate phase-out reduction
            excess_income = max_(md_agi - p.phase_out.threshold[filing_status], 0)
            phase_out_reduction = excess_income * p.phase_out.rate

            # Apply phase-out (itemized deductions cannot go below zero)
            return max_(base_itemized - phase_out_reduction, 0)

        # When phase-out does not apply, no phase-out
        return base_itemized
