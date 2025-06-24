from policyengine_us.model_api import *


class md_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = [
        "https://govt.westlaw.com/mdc/Document/N05479690A64A11DBB5DDAC3692B918BC?viewType=FullText&originationContext=documenttoc&transitionType=CategoryPageItem&contextData=(sc.Default)",
        "https://www.marylandtaxes.gov/forms/21_forms/Resident_Booklet.pdf#page=5",
        "https://www.marylandtaxes.gov/forms/22_forms/Resident_Booklet.pdf#page=5",
        "https://mgaleg.maryland.gov/Pubs/BudgetFiscal/2025rs-budget-docs-operating-cc-summary.pdf#page=17",  # FY 2025 Budget changes
    ]
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        # Base itemized deductions (federal itemized deductions less SALT plus capped property taxes)
        base_itemized = add(
            tax_unit,
            period,
            ["itemized_deductions_less_salt", "capped_property_taxes"],
        )

        # Starting in 2025, apply income-based phase-out
        if period.start.year >= 2025:
            filing_status = tax_unit("filing_status", period)
            md_agi = tax_unit("md_agi", period)

            p = parameters(period).gov.states.md.tax.income.deductions.itemized
            threshold = p.phase_out_threshold[filing_status]
            phase_out_rate = p.phase_out_rate

            # Calculate phase-out reduction
            excess_income = max_(md_agi - threshold, 0)
            phase_out_reduction = excess_income * phase_out_rate

            # Apply phase-out (itemized deductions cannot go below zero)
            return max_(base_itemized - phase_out_reduction, 0)

        # For years before 2025, no phase-out
        return base_itemized
