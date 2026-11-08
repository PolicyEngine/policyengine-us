from policyengine_us.model_api import *


class mn_elderly_disabled_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota elderly/disabled subtraction"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Schedule M1R. Minn. Stat. 290.0802 reduces the base amount by the "
        "nontaxable retirement and disability benefits of subd. 1(c), which "
        "take in all of the head's and spouse's railroad retirement benefits, "
        "and measures adjusted gross income (subd. 1(a)) without the railroad "
        "benefits in federal gross income, which 45 U.S.C. 231m(a) keeps the "
        "state from taxing."
    )
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290.0802",
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1r_21.pdf",
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1r_22.pdf",
        "https://www.revenue.state.mn.us/sites/default/files/2026-07/m1r-25.pdf",
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        mn_itax = parameters(period).gov.states.mn.tax.income
        p = mn_itax.subtractions.elderly_disabled
        filing_status = tax_unit("filing_status", period)
        # calculate the subtraction amount
        # ... determine age eligibility
        person = tax_unit.members
        is_elderly = person("age", period) >= p.minimum_age
        is_head = person("is_tax_unit_head", period)
        elderly_head = is_head & is_elderly
        is_spouse = person("is_tax_unit_spouse", period)
        elderly_spouse = is_spouse & is_elderly
        # ... determine disability eligiblity
        is_disabled = person("is_permanently_and_totally_disabled", period)
        disabled_head = is_head & is_disabled
        disabled_spouse = is_spouse & is_disabled
        # ... determine base subtraction amount
        base_amount = where(
            tax_unit.any(elderly_head | elderly_spouse),
            p.base_amount[filing_status],
            0,  # because federally-taxable disability income
            # included in federal Form 1040, line 1z, is unknown
        )
        # ... determine disability income as on federal Schedule R
        is_dependent = person("is_tax_unit_dependent", period)
        dinc_person = person("total_disability_payments", period)
        disinc_person = dinc_person * ~is_dependent * ~is_elderly
        disability_income = tax_unit.sum(disinc_person)
        # ... determine nontaxable retirement and disability benefits,
        # subd. 1(c): the amounts section 22(c)(3) counts, which include the
        # title II and tier 1 benefits section 86 leaves out and the tax-free
        # rest of the railroad annuity (as section_22_income reads it), plus
        # the pension and annuity benefits in federal gross income that the
        # state cannot tax, the taxable railroad benefits. Section 22(c)(3)
        # counts what the individual, or either spouse on a joint return,
        # receives, so a dependent's benefits stay out.
        unit_socsec = tax_unit_non_dep_add(tax_unit, period, ["social_security"])
        unit_taxed_socsec = add(tax_unit, period, ["taxable_social_security"])
        untaxed_social_security = max_(0, unit_socsec - unit_taxed_socsec)
        railroad_retirement_benefits = tax_unit_non_dep_add(
            tax_unit,
            period,
            [
                "railroad_social_security_equivalent_benefits",
                "taxable_railroad_pension_benefits",
                "tax_exempt_railroad_pension_benefits",
            ],
        )
        # ... determine total disability and retirement benefits
        benefits = (
            disability_income + untaxed_social_security + railroad_retirement_benefits
        )
        # ... subtract benefits from base amount
        amount = max_(0, base_amount - benefits)
        # ... determine net agi: subd. 1(a) adds lump-sum distributions to
        # federal AGI and takes out the railroad benefits that federal gross
        # income includes.
        fed_agi = tax_unit("adjusted_gross_income", period)
        lump_sum = tax_unit("form_4972_lumpsum_distributions", period)
        exempt_railroad = add(tax_unit, period, ["taxable_railroad_benefits"])
        agi = fed_agi + lump_sum - exempt_railroad
        agi_offset_base = p.agi_offset_base[filing_status]
        joint = filing_status == filing_status.possible_values.JOINT
        head_eligible = tax_unit.any(elderly_head | disabled_head)
        spouse_eligible = tax_unit.any(elderly_spouse | disabled_spouse)
        eligible = head_eligible | spouse_eligible
        joint_with_two_eligibles = joint & head_eligible & spouse_eligible
        agi_offset_extra = joint_with_two_eligibles * p.agi_offset_extra
        agi_offset = agi_offset_base + agi_offset_extra
        net_agi = max_(0, agi - agi_offset)
        fraction_of_net_agi = p.net_agi_fraction * net_agi
        # ... subtract fracton_of_net_agi from amount to get final amount
        final_amount = max_(0, amount - fraction_of_net_agi)
        return eligible * final_amount
