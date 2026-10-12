from policyengine_us.model_api import *


class id_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-01-2023.pdf#page=8",
        "https://tax.idaho.gov/wp-content/uploads/forms/EFO00089/EFO00089_09-23-2021.pdf",
        "https://legislature.idaho.gov/statutesrules/idstat/Title63/T63CH30/SECT63-3022/",  # Idaho Code 63-3022 (subtractions/itemized framework)
        "https://tax.idaho.gov/wp-content/uploads/forms/EFO00088/EFO00088_03-02-2026.pdf#page=13",  # Idaho Form 39R - Additions and Subtractions instructions (foreign-tax addback rule)
        "https://www.govinfo.gov/content/pkg/PLAW-119publ21/html/PLAW-119publ21.htm",  # P.L. 119-21, sec. 70111 (IRC 68, from 2026)
    )
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        # Supplied Schedule A totals already represent the claimant's
        # actual deductions, even if component expenses are incomplete.
        # Check their provenance before calculating either aggregate.
        supplied_itemized = has_input_for_period(
            tax_unit.simulation, "itemized_taxable_income_deductions", period
        ) or has_input_for_period(
            tax_unit.simulation, "total_itemized_taxable_income_deductions", period
        )
        # Idaho reduces the federal itemized deductions by the SALT deduction.
        # When foreign tax is claimed as a federal itemized deduction, it is
        # already in itemized_taxable_income_deductions; when claimed as a
        # federal credit (Form 1116), it is not in itemized deductions and
        # there is nothing to add back. Idaho Form 39R instructions
        # ("Do not include foreign taxes as a subtraction, since they're
        # claimed as part of the Idaho itemized deduction, if allowable")
        # are consistent with no unconditional addback here.
        id_salt_ded = tax_unit("id_salt_deduction", period)
        itemized_ded = tax_unit("itemized_taxable_income_deductions", period)
        if supplied_itemized:
            return max_(0, itemized_ded - id_salt_ded)
        federal_medical = tax_unit("medical_expense_deduction", period)
        claimant_medical = tax_unit(
            "id_health_insurance_premiums_medical_deduction", period
        )
        medical_adjustment = federal_medical - claimant_medical

        # Correct the medical component of derived itemized totals as well as
        # premium overlap, so dependent-paid costs do not remain deducted here.
        limitation_adjustment = 0
        p = parameters(period).gov.irs.deductions.itemized.limitation
        if p.applies and p.obbb.applies:
            # IRC 68 applies after the medical deduction is limited. Removing
            # invalid medical costs can also reduce the 2/37 limitation.
            total = tax_unit("total_itemized_taxable_income_deductions", period)
            corrected_total = max_(0, total - medical_adjustment)
            filing_status = tax_unit("filing_status", period)
            threshold = parameters(period).gov.irs.income.bracket.thresholds["6"][
                filing_status
            ]
            agi = tax_unit("adjusted_gross_income", period)
            exemptions = tax_unit("exemptions", period)
            excess = max_(0, agi - exemptions - threshold)
            limitation_adjustment = p.obbb.rate * (
                min_(total, excess) - min_(corrected_total, excess)
            )
        # The legacy Pease ceiling excludes medical deductions, so its
        # reduction does not change when this medical component is corrected.
        return max_(
            0,
            itemized_ded - medical_adjustment + limitation_adjustment - id_salt_ded,
        )
