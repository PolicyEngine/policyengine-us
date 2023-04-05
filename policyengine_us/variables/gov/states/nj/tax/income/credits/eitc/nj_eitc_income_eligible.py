from policyengine_us.model_api import *


class nj_eitc_age_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "New Jersey Eligible for EITC"
    definition_period = YEAR
    reference = "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-4-7/"
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # Get parameter tree for federal EITC.
        p = parameters(period).gov.irs.credits.eitc

        # Determine if filer is above federal EITC income threshold.
        # We can find the income threshold by looking at their filing status and the phase-out rate for 0 children.
        # Note: this assumes the same phaseout rate for all filing statuses (which is the case).
        is_joint = tax_unit("tax_unit_is_joint", period)
        joint_bonus = p.phase_out.joint_bonus.calc(0)
        phaseout_rate = p.phase_out.rate.calc(0)
        phaseout_start = p.phase_out.start.calc(0) + is_joint * joint_bonus
        max_credit = p.max.calc(0)
        completed_phaseout = max_credit / phaseout_rate + phaseout_start
        return tax_unit("adjusted_gross_income", period) < completed_phaseout
