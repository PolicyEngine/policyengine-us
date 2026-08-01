from policyengine_us.model_api import *


class vt_retirement_income_exemption_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Vermont retirement income exemption eligibility status"
    reference = (
        "https://legislature.vermont.gov/statutes/section/32/151/05811",  # Titl. 32 V.S.A. § 5811(21)(B)(iv)
        "https://legislature.vermont.gov/statutes/section/32/151/05830e"  # Titl. 32 V.S.A. § 5830e
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112%20Instr-2022.pdf#page=3",  # Instruction for 2022 SCHEDULE IN-112 - RETIREMENT INCOME EXEMPTION WORKSHEET
        "https://tax.vermont.gov/individuals/seniors-and-retirees",  # Instruction for exemption from different retirement system
    )
    defined_for = StateCode.VT
    documentation = "Vermont filers use below criteria to check whether the tax unit is eligible for vermont retirement income exemption."

    def formula(tax_unit, period, parameters):
        # Filer can choose from one of Social Security,
        # Civil Service Retirement System (CSRS), Military Retirement Income
        # or other eligible retirement systems to determine eligibility
        filing_status = tax_unit("filing_status", period)
        agi = tax_unit("adjusted_gross_income", period)
        p = parameters(period).gov.states.vt.tax.income.agi.retirement_income_exemption
        # One of the retirement income should be greater than 0
        retirement_income = add(
            tax_unit,
            period,
            [
                "tax_unit_taxable_social_security",
                "military_retirement_pay",
                "csrs_retirement_pay",
            ],
        )
        retirement_income_qualified = retirement_income > 0
        # Determine which retirement system the filer uses, mirroring the
        # main exemption formula, so the eligibility gate uses the matching
        # phase-out threshold (Social Security thresholds differ from CSRS
        # under 2025 Act 71).
        tax_unit_taxable_social_security = tax_unit(
            "tax_unit_taxable_social_security", period
        )
        vt_military_retirement_pay_exclusion = tax_unit(
            "vt_military_retirement_pay_exclusion", period
        )
        vt_csrs_retirement_pay_exclusion = tax_unit(
            "vt_csrs_retirement_pay_exclusion", period
        )

        def phased_exemption(amount, reduction_start, reduction_end):
            partial_qualified = (
                (agi >= reduction_start) & (agi < reduction_end) & (amount != 0)
            )
            partial_exemption_ratio = max_(reduction_end - agi, 0) / p.divisor
            partial_exemption_ratio = round_(partial_exemption_ratio, 2)
            partial_exemption_ratio = min_(partial_exemption_ratio, 1)
            partial_exemption = amount * partial_exemption_ratio
            full_exemption = where(agi < reduction_start, amount, 0)
            return where(partial_qualified, partial_exemption, full_exemption)

        larger_retirement_income = max_(
            tax_unit_taxable_social_security,
            vt_military_retirement_pay_exclusion,
        )
        chosen_retirement_income = max_(
            larger_retirement_income, vt_csrs_retirement_pay_exclusion
        )
        use_ss = tax_unit_taxable_social_security == chosen_retirement_income
        ss_reduction_end = p.social_security.reduction.end[filing_status]
        csrs_reduction_end = p.csrs.reduction.end[filing_status]
        reduction_end = where(
            use_ss,
            ss_reduction_end,
            csrs_reduction_end,
        )
        # The agi should below threshold
        agi_qualified = agi < reduction_end
        # The 2025 Act 71 income-based military exclusion (32 V.S.A. 5830e(d))
        # may be taken in addition to one elected exclusion from subsections
        # (a)-(c), so the non-military AGI gate only controls that component.
        use_military = ~use_ss & (
            vt_military_retirement_pay_exclusion == chosen_retirement_income
        )
        military_income_based = p.military_retirement.income_based_structure.in_effect
        agi_qualified = where(
            use_military & military_income_based, True, agi_qualified
        )
        single_election_eligible = retirement_income_qualified & agi_qualified
        ss_exemption = phased_exemption(
            tax_unit_taxable_social_security,
            p.social_security.reduction.start[filing_status],
            ss_reduction_end,
        )
        csrs_exemption = phased_exemption(
            vt_csrs_retirement_pay_exclusion,
            p.csrs.reduction.start[filing_status],
            csrs_reduction_end,
        )
        act_71_eligible = (
            (vt_military_retirement_pay_exclusion > 0)
            | (ss_exemption > 0)
            | (csrs_exemption > 0)
        )
        # Both qualified then the filer is qualified for vermont retirement
        # income exemption
        return where(
            military_income_based, act_71_eligible, single_election_eligible
        )
