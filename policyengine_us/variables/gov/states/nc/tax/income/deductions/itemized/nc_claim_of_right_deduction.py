from policyengine_us.model_api import *


class nc_claim_of_right_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina claim of right repayment itemized deduction"
    unit = USD
    documentation = (
        "North Carolina itemized deduction for repaying income included in "
        "adjusted gross income in an earlier year under a claim of right. "
        "Repayments above the threshold are deductible in full. Smaller "
        "repayments are reduced by two percent of federal adjusted gross "
        "income less the taxpayer's other miscellaneous itemized deductions. "
        "Not modeled: the bar on the deduction when federal tax for the year "
        "of repayment is computed under 26 U.S.C. 1341(a)(5)."
    )
    definition_period = YEAR
    reference = (
        # N.C. Gen. Stat. 105-153.5(a)(2)d
        "https://www.ncleg.gov/EnactedLegislation/Statutes/HTML/BySection/Chapter_105/GS_105-153.5.html",
        # 2016 Form D-401 instructions, Repayment of Claim of Right Worksheet
        "https://taxsim.nber.org/historical_state_tax_forms/NC/2016/D401.pdf#page=13",
        # 2025 Form D-401 instructions, Form D-400 Schedule A line 8 and worksheet
        "https://www.ncdor.gov/2025-d-401-individual-income-tax-instructions/open#page=20",
    )
    defined_for = StateCode.NC

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # A dependent's repayment belongs on the dependent's own return.
        repayment = tax_unit.sum(
            person("claim_of_right_repayment", period)
            * person("is_tax_unit_head_or_spouse", period)
        )
        p = parameters(period).gov.states.nc.tax.income.deductions.itemized
        # Repayments of $3,000 or less are reduced by (i) the section 67(a)
        # floor, two percent of federal AGI, minus (ii) the other
        # miscellaneous itemized deductions, not below zero. Section 67(g)
        # disallows those other deductions from 2018, so the 2018-and-later
        # worksheet subtracts the whole floor.
        p_misc = parameters(period).gov.irs.deductions.itemized.misc
        floor = p_misc.floor * tax_unit("positive_agi", period)
        if p_misc.applies:
            other_misc_deductions = tax_unit("total_misc_deductions", period)
        else:
            other_misc_deductions = 0
        remaining_floor = max_(floor - other_misc_deductions, 0)
        small_repayment_deduction = max_(repayment - remaining_floor, 0)
        return where(
            repayment > p.claim_of_right.threshold,
            repayment,
            small_repayment_deduction,
        )
