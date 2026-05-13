from policyengine_us.model_api import *


class lifetime_learning_credit_phase_out(Variable):
    value_type = float
    entity = TaxUnit
    label = "Lifetime Learning Credit phase-out"
    unit = "/1"
    documentation = (
        "Fraction of the Lifetime Learning Credit that is phased out "
        "based on AGI. Before 2021 the LLC had lower phase-out thresholds "
        "than the American Opportunity Credit (IRS Form 8863, Part II); "
        "the Consolidated Appropriations Act, 2021 harmonized them "
        "(IRC 25A(i))."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25A#d_1"

    def formula(tax_unit, period, parameters):
        llc = parameters(period).gov.irs.credits.education.lifetime_learning_credit
        agi = tax_unit("adjusted_gross_income", period)
        is_joint = tax_unit("tax_unit_is_joint", period)
        phase_out_start = where(
            is_joint,
            llc.phase_out.start.joint,
            llc.phase_out.start.single,
        )
        phase_out_length = where(
            is_joint,
            llc.phase_out.length.joint,
            llc.phase_out.length.single,
        )
        excess_agi = max_(0, agi - phase_out_start)
        return min_(1, excess_agi / phase_out_length)
