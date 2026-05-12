from policyengine_us.model_api import *


class me_pension_income_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine pension income deduction"
    unit = USD
    documentation = "Maine pension income deduction, which subtracts from federal AGI to compute Maine AGI."
    definition_period = YEAR
    defined_for = StateCode.ME
    reference = "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_1s_ff.pdf"

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
        relevant = where(is_joint, is_head | is_spouse, is_head)
        total_non_military = tax_unit.sum(where(relevant, non_military_deduction, 0))
        total_military = tax_unit.sum(where(relevant, military_retirement_pay, 0))

        # Phaseout fraction (Worksheet for Phaseout of Non-Military Pension
        # Income Deduction). Military retirement pay is not phased out per
        # 36 M.R.S. § 5122(2)(LL).
        agi = tax_unit("adjusted_gross_income", period)
        start = p.phaseout.start[filing_status]
        length = p.phaseout.length[filing_status]
        excess = max_(agi - start, 0)
        phaseout_fraction = min_(excess / length, 1)
        allowed_non_military = total_non_military * (1 - phaseout_fraction)
        return allowed_non_military + total_military
