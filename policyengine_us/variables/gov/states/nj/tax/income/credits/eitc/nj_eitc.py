from policyengine_us.model_api import *


class nj_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-4-7/"
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # Get parameter tree for NJ EITC.
        p = parameters(period).gov.states.nj.tax.income.credits.eitc

        # Get parameter tree for federal EITC.
        p_fed = parameters(period).gov.irs.credits.eitc

        # Determine if filer is above federal EITC income threshold.
        # We can find the income threshold by looking at their filing status and the phase-out rate for 0 children.
        # Note: this assumes the same phaseout rate for all filing statuses (which is the case).
        is_joint = tax_unit("tax_unit_is_joint", period)
        joint_bonus = p_fed.phase_out.joint_bonus.calc(0)
        phaseout_rate = p_fed.phase_out.rate.calc(0)
        phaseout_start = p_fed.phase_out.start.calc(0) + is_joint * joint_bonus
        max_credit = p_fed.max.calc(0)
        completed_phaseout = max_credit / phaseout_rate + phaseout_start
        income_eligible = (
            tax_unit("adjusted_gross_income", period) < completed_phaseout
        )

        # Calculate NJ EITC.
        # If eligible for federal EITC, return federal EITC * percent_of_federal_eitc.
        # If ineligible for federal EITC only because of age, return max federal EITC * percent_of_federal_eitc.
        #     Note: this implies that they have no children (hence the max federal EITC input).
        # Otherwise, return 0.
        # Worksheet reference: https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=43
        nj_eitc = select(
            [
                tax_unit("eitc_eligible", period),
                income_eligible & tax_unit("nj_eitc_eligible", period),
            ],
            [
                tax_unit("eitc", period),
                max_credit,
            ],
            default=0,
        )

        return nj_eitc * p.percent_of_federal_eitc
