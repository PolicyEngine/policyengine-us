from policyengine_us.model_api import *
from policyengine_us.tools.period_branch import has_input
from policyengine_us.tools.state_itemization import joint_itemization_is_enabled


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
        # Tax-General 10-218(b)(1) and (b)(3): federal itemized deductions,
        # less income taxes net of their pro rata share of the section 68
        # reduction.
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-218&enactments=false",
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=21",
        "https://services.marylandcomptroller.gov/taxes/en/what-s-new-for-the-2026-tax-filing-season-2025-tax-year?id=kb_article_view&sysparm_article=KB0010023",
        # Section 68 as amended by P.L. 119-21, sec. 70111, from 2026.
        # PDF pages 94-95
        "https://www.govinfo.gov/content/pkg/PLAW-119publ21/pdf/PLAW-119publ21.pdf#page=94",
    ]
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        # Base itemized deductions (federal itemized deductions less SALT plus capped property taxes)
        base_itemized = add(
            tax_unit,
            period,
            ["itemized_deductions_less_salt", "capped_property_taxes"],
        )
        return _limit_deductions(tax_unit, period, parameters, base_itemized)

    def formula_2025(tax_unit, period, parameters):
        simulation = tax_unit.simulation
        if (
            has_input(simulation, "capped_property_taxes", period)
            and not joint_itemization_is_enabled(period, parameters)
            and not any(
                has_input(simulation, variable, period)
                for variable in (
                    "state_and_local_sales_tax_elected",
                    "state_sales_tax",
                    "local_sales_tax",
                )
            )
        ):
            # A supplied capped property amount can stand in for the entire
            # eligible SALT component when no sales-tax detail was supplied.
            return md_itemized_deductions.formula(tax_unit, period, parameters)

        # Form 502 line 17b removes only income taxes. The Comptroller
        # accepts counting property taxes first under the federal SALT cap.
        property_tax = min_(
            tax_unit("capped_property_taxes", period), tax_unit("salt_cap", period)
        )
        elects_sales_tax = tax_unit("state_and_local_sales_tax_elected", period)
        deductible_salt = where(
            elects_sales_tax, tax_unit("salt_deduction", period), property_tax
        )
        base_itemized = (
            tax_unit("itemized_deductions_less_salt", period) + deductible_salt
        )
        return _limit_deductions(tax_unit, period, parameters, base_itemized)


def _limit_deductions(tax_unit, period, parameters, base_itemized):
    if parameters(period).gov.irs.deductions.itemized.limitation.obbb.applies:
        # Tax-General 10-218(b)(1) starts from federal itemized deductions
        # after the section 68 reduction R, and 10-218(b)(3) subtracts
        # the income taxes I net of their pro rata share of R:
        # T - R - I + R * I / T, where T is the pre-reduction total.
        # With I = T - base this equals base * (1 - R / T).
        # A sales election has no income taxes to restore.
        total = tax_unit("total_itemized_taxable_income_deductions", period)
        reduction = tax_unit("itemized_taxable_income_deductions_reduction", period)
        mask = total > 0
        reduction_share = np.zeros_like(total)
        reduction_share[mask] = reduction[mask] / total[mask]
        base_itemized = base_itemized * (1 - reduction_share)

    p = parameters(period).gov.states.md.tax.income.deductions.itemized
    if p.phase_out.applies:
        filing_status = tax_unit("filing_status", period)
        md_agi = tax_unit("adjusted_gross_income", period)
        excess_income = max_(md_agi - p.phase_out.threshold[filing_status], 0)
        return max_(base_itemized - excess_income * p.phase_out.rate, 0)

    return base_itemized
