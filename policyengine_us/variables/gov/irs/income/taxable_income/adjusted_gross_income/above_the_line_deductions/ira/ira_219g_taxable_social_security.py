from policyengine_us.model_api import *


class ira_219g_taxable_social_security(Variable):
    """Section 86 taxable benefits figured without the IRA deduction.

    Pub. 590-A Appendix B, Worksheet 1 lines 1-17. Same inputs and thresholds as
    the engine's taxable_ss_magi / tax_unit_taxable_social_security, except that
    the IRA deduction is not subtracted (it is what is being computed).
    """

    value_type = float
    entity = TaxUnit
    label = "Taxable Social Security for 219(g) MAGI (before the IRA deduction)"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/219#g_3_A",
        "https://www.irs.gov/publications/p590a",
    )

    def formula(tax_unit, period, parameters):
        irs = parameters(period).gov.irs
        p = irs.social_security.taxability
        # taxable_ss_magi, with the IRA deduction removed from the ALDs.
        sources = [
            s
            for s in irs.gross_income.sources
            if s not in ["taxable_social_security", "taxable_unemployment_compensation"]
        ]
        if "taxable_unemployment_compensation" in irs.gross_income.sources:
            sources.append("unemployment_compensation")
        sources.append("tax_exempt_interest_income")
        person = tax_unit.members
        not_dependent = ~person("is_tax_unit_dependent", period)
        gross = 0
        for source in sources:
            gross += not_dependent * max_(0, add(person, period, [source]))
        gross = tax_unit.sum(gross)
        gross += tax_unit("section_911_excluded_income", period)
        if parameters(period).gov.contrib.ubi_center.basic_income.taxable:
            gross += add(tax_unit, period, ["basic_income"])
        revoked = p.income.revoked_deductions
        deductions = [
            d
            for d in irs.ald.deductions
            if d not in revoked and d not in irs.ald.ira.magi_excluded_deductions
        ]
        total_deductions = tax_unit_non_dep_add(
            tax_unit,
            period,
            deductions,
            include_dependents=irs.ald.filer_amounts_recorded_on_dependents,
        )
        ss_magi = max_(0, gross - total_deductions)
        # tax_unit_taxable_social_security, with that MAGI.
        gross_ss = tax_unit("tax_unit_social_security_for_taxability", period)
        combined = ss_magi + p.combined_income_ss_fraction * gross_ss
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        cohabitating = tax_unit("cohabitating_spouses", period)
        base = where(
            separate & cohabitating,
            p.threshold.base.separate_cohabitating,
            p.threshold.base.main[filing_status],
        )
        adjusted_base = where(
            separate & cohabitating,
            p.threshold.adjusted_base.separate_cohabitating,
            p.threshold.adjusted_base.main[filing_status],
        )
        excess = max_(0, combined - base)
        over_adjusted = max_(0, combined - adjusted_base)
        tier1 = min_(p.rate.base.benefit_cap * gross_ss, p.rate.base.excess * excess)
        bracket = min_(tier1, p.rate.additional.bracket * (adjusted_base - base))
        tier2 = min_(
            p.rate.additional.excess * over_adjusted + bracket,
            p.rate.additional.benefit_cap * gross_ss,
        )
        return select(
            [combined < base, combined < adjusted_base], [0, tier1], default=tier2
        )
