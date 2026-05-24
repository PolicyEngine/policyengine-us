from policyengine_us.model_api import *


class me_pension_income_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine pension income deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ME
    reference = "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/25_1040me_sch_1s_fillable.pdf#page=2"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(
            period
        ).gov.states.me.tax.income.agi.subtractions.pension_exclusion

        # Per-person non-military pension deduction (Pension Income Deduction
        # Worksheet, lines P1-P5).
        pension_income = person("pension_income", period)
        gross_ss = person("social_security", period)
        ss_reduced_cap = max_(p.cap - gross_ss, 0)
        non_military_deduction = min_(pension_income, ss_reduced_cap)

        military_retirement_pay = person("military_retirement_pay", period)

        # Restrict to the head (and spouse if filing jointly) per Schedule 1S
        # line 4.
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        filing_status = tax_unit("filing_status", period)
        is_joint = filing_status == filing_status.possible_values.JOINT
        non_military_head_only = tax_unit.sum(where(is_head, non_military_deduction, 0))
        non_military_with_spouse = tax_unit.sum(
            where(is_head | is_spouse, non_military_deduction, 0)
        )
        total_non_military = where(
            is_joint, non_military_with_spouse, non_military_head_only
        )
        military_head_only = tax_unit.sum(where(is_head, military_retirement_pay, 0))
        military_with_spouse = tax_unit.sum(
            where(is_head | is_spouse, military_retirement_pay, 0)
        )
        total_military = where(is_joint, military_with_spouse, military_head_only)

        # Phaseout fraction (Worksheet for Phaseout of Non-Military Pension
        # Income Deduction). Military retirement pay is fully deducted
        # under 36 M.R.S. § 5122(2)(M-2)(1)(b) and is not reduced by the
        # § 5122(2)(M-3) phaseout.
        agi = tax_unit("adjusted_gross_income", period)
        start = p.phaseout.start[filing_status]
        width = p.phaseout.width[filing_status]
        excess = max_(agi - start, 0)
        phaseout_fraction = min_(excess / width, 1)
        allowed_non_military = total_non_military * (1 - phaseout_fraction)
        return allowed_non_military + total_military
