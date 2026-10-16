from policyengine_us.model_api import *


class nc_claim_of_right_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina claim of right repayment itemized deduction"
    unit = USD
    documentation = (
        "North Carolina itemized deduction for repaying income included in "
        "adjusted gross income in an earlier year under a claim of right; from "
        "2026, only income North Carolina taxed that year. Repayments above "
        "the threshold are deductible in full. Smaller repayments are reduced "
        "by two percent of federal adjusted gross income less the filers' "
        "other miscellaneous itemized deductions. No deduction is allowed "
        "when federal tax for the year of repayment is computed under 26 "
        "U.S.C. 1341(a)(5). Not modeled: from 2026, repayments of amounts "
        "North Carolina added to adjusted gross income that federal law "
        "excluded."
    )
    definition_period = YEAR
    reference = (
        # N.C. Gen. Stat. 105-153.5(a)(2)d
        "https://www.ncleg.gov/EnactedLegislation/Statutes/HTML/BySection/Chapter_105/GS_105-153.5.html",
        # S.L. 2026-31, section 1.8, PDF pages 5-6
        "https://www.ncleg.gov/EnactedLegislation/SessionLaws/PDF/2025-2026/SL2026-31.pdf#page=5",
        # 2016 Form D-401 instructions, Repayment of Claim of Right Worksheet
        "https://taxsim.nber.org/historical_state_tax_forms/NC/2016/D401.pdf#page=13",
        # 2025 Form D-401 instructions, Form D-400 Schedule A line 8 and worksheet
        "https://www.ncdor.gov/2025-d-401-individual-income-tax-instructions/open#page=20",
    )
    defined_for = StateCode.NC

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.nc.tax.income.deductions.itemized
        repaid = person("claim_of_right_repayment", period)
        if p.claim_of_right.nc_modified_income_basis:
            # From 2026, only repayments of amounts included in AGI as
            # modified for North Carolina in the earlier year.
            excluded = person(
                "nc_claim_of_right_repayment_excluded_from_income", period
            )
            repaid = max_(repaid - excluded, 0)
        # Dependents' repayments and expenses belong on their own returns.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        repayment = tax_unit.sum(repaid * head_or_spouse)
        # Repayments of $3,000 or less are reduced by (i) the section 67(a)
        # floor, two percent of federal AGI, minus (ii) the other
        # miscellaneous itemized deductions, not below zero. Section 67(g)
        # disallows those other deductions from 2018, so the 2018-and-later
        # worksheet subtracts the whole floor.
        p_misc = parameters(period).gov.irs.deductions.itemized.misc
        floor = p_misc.floor * tax_unit("positive_agi", period)
        if p_misc.applies:
            other_misc_deductions = tax_unit.sum(
                add(person, period, p_misc.sources) * head_or_spouse
            )
        else:
            other_misc_deductions = 0
        remaining_floor = max_(floor - other_misc_deductions, 0)
        small_repayment_deduction = max_(repayment - remaining_floor, 0)
        deduction = where(
            repayment > p.claim_of_right.threshold,
            repayment,
            small_repayment_deduction,
        )
        # No deduction when federal tax for the year of repayment is
        # computed under section 1341(a)(5); G.S. 105-266.2 instead treats
        # the prior-year North Carolina tax on the item as a payment.
        credit_applies = tax_unit("claim_of_right_credit_applies", period)
        return where(credit_applies, 0, deduction)
