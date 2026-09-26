from policyengine_us.model_api import *


class nj_eitc_income_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "New Jersey Eligible for EITC"
    definition_period = YEAR
    reference = (
        "https://pub.njleg.gov/bills/2020/PL21/130_.PDF#page=2",
        "https://www.nj.gov/treasury/taxation/pdf/other_forms/tgi-ee/2024/1040i.pdf#page=44",
    )
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # N.J.S.A. 54A:4-7a.(4) requires filers on the age-expanded path to
        # "meet all qualifications, except for the minimum or maximum age,
        # for the federal earned income tax credit". That includes the
        # federal investment income test, so reuse the federal
        # disqualified-income measure (Pub 596 Worksheet 1 baskets) rather
        # than a separate sum that lets rental or passive losses offset
        # interest and dividends.
        p = parameters(period).gov.irs.credits.eitc
        investment_income_eligible = tax_unit("eitc_investment_income_eligible", period)

        # Determine if filer is above federal EITC income threshold.
        # We can find the income threshold by looking at their filing status and the phase-out rate for 0 children.
        # Note: this assumes the same phaseout rate for all filing statuses (which is the case).
        is_joint = tax_unit("tax_unit_is_joint", period)
        joint_bonus = p.phase_out.joint_bonus.calc(0)
        phaseout_rate = p.phase_out.rate.calc(0)
        phaseout_start = p.phase_out.start.calc(0) + is_joint * joint_bonus
        max_credit = p.max.calc(0)
        completed_phaseout = max_credit / phaseout_rate + phaseout_start
        return (
            tax_unit("adjusted_gross_income", period) < completed_phaseout
        ) & investment_income_eligible
