from policyengine_us.model_api import *


class capped_qualified_tuition_expenses_ald(Variable):
    value_type = float
    entity = TaxUnit
    label = "Qualified tuition expenses above-the-line deduction (capped)"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Tuition and fees above-the-line deduction from IRS Form 8917 "
        "(pre-2021 only). Applies the IRC 222(b)(2) cap using a locally "
        "computed MAGI to avoid a circular dependency on "
        "`adjusted_gross_income`."
    )
    reference = (
        "https://www.irs.gov/pub/irs-pdf/f8917.pdf#page=2"
        # Law was repealed starting tax year 2021.
        "https://irc.bloombergtax.com/public/uscode/doc/irc/section_222"
    )

    def formula(tax_unit, period, parameters):
        # This variable contributes to the ALD list only in years when
        # `capped_qualified_tuition_expenses_ald` is listed in
        # `gov.irs.ald.deductions`. If a reform removes it, return 0.
        all_alds = parameters(period).gov.irs.ald.deductions
        if "capped_qualified_tuition_expenses_ald" not in all_alds:
            return 0
        # Married filing separately cannot take the tuition deduction.
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        qualified_tuition_expenses = add(
            tax_unit, period, ["qualified_tuition_expenses"]
        )
        # Build a simple MAGI from non-dependent person-level income sources,
        # excluding sources that depend on MAGI themselves (taxable SS, UI).
        irs = parameters(period).gov.irs
        gross_income_sources = irs.gross_income.sources
        person = tax_unit.members
        not_dependent = ~person("is_tax_unit_dependent", period)
        cycle_sources = {
            "taxable_social_security",
            "taxable_unemployment_compensation",
        }
        safe_sources = [src for src in gross_income_sources if src not in cycle_sources]
        if "taxable_unemployment_compensation" in gross_income_sources:
            safe_sources.append("unemployment_compensation")
        magi = 0
        for source in safe_sources:
            magi += not_dependent * max_(0, add(person, period, [source]))
        magi = tax_unit.sum(magi)
        p = parameters(period).gov.irs.deductions.tuition_and_fees
        joint = filing_status == filing_status.possible_values.JOINT
        cap = where(joint, p.joint.calc(magi), p.non_joint.calc(magi))
        return where(separate, 0, min_(qualified_tuition_expenses, cap))
