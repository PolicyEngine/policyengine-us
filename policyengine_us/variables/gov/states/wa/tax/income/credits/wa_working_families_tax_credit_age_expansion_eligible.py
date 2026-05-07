from policyengine_us.model_api import *


class wa_working_families_tax_credit_age_expansion_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for Washington Working Families Tax Credit via age expansion"
    definition_period = YEAR
    reference = "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Passed%20Legislature/6346-S.PL.pdf#page=60"
    defined_for = StateCode.WA

    def formula(tax_unit, period, parameters):
        # ESSB 6346 Sec. 901(2)(a)(ii)(D): individuals who would otherwise
        # qualify for EITC except for age can qualify if at least age 18.
        p = parameters(
            period
        ).gov.states.wa.tax.income.credits.working_families_tax_credit.age_expansion

        expansion_in_effect = p.in_effect
        person = tax_unit.members
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        filer_meets_min_age = (age_head >= p.min_age) | (age_spouse >= p.min_age)
        investment_income_eligible = tax_unit("eitc_investment_income_eligible", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        has_tin = person("has_tin", period)
        filers_have_tin = tax_unit.sum(is_head_or_spouse & ~has_tin) == 0
        child_count = tax_unit.sum(
            person("is_qualifying_child_dependent", period) & has_tin
        )
        eitc = parameters(period).gov.irs.credits.eitc
        earnings = tax_unit("filer_adjusted_earnings", period)
        agi = tax_unit("adjusted_gross_income", period)
        maximum = eitc.max.calc(child_count)
        phased_in = min_(maximum, earnings * eitc.phase_in_rate.calc(child_count))
        phase_out_start = eitc.phase_out.start.calc(child_count)
        phase_out_start += tax_unit("tax_unit_is_joint", period) * eitc.phase_out.joint_bonus.calc(
            child_count
        )
        reduction = max_(0, max_(earnings, agi) - phase_out_start) * eitc.phase_out.rate.calc(
            child_count
        )
        eitc_amount_before_take_up = min_(phased_in, max_(0, maximum - reduction))

        return (
            expansion_in_effect
            & filer_meets_min_age
            & investment_income_eligible
            & filers_have_tin
            & (eitc_amount_before_take_up > 0)
        )
