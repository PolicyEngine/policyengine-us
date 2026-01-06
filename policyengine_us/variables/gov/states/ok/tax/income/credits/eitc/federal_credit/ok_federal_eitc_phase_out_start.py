from policyengine_us.model_api import *


class ok_federal_eitc_phase_out_start(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal EITC phase-out start for the Oklahoma EITC computation"
    unit = USD
    definition_period = YEAR
    reference = (
        # Oklahoma Statutes 68 O.S. Section 2357.43
        "https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/",
    )
    defined_for = StateCode.OK
    documentation = """
    Federal EITC phase-out start threshold using FROZEN 2020 parameters.

    The phase-out start is the income level at which the EITC begins to
    reduce. Joint filers receive a bonus that increases this threshold.

    2020 Phase-out start by number of children (single filers):
    - 0 children: $8,790
    - 1 child: $19,330
    - 2 children: $19,330
    - 3+ children: $19,330

    2020 Joint filing bonus:
    - 0 children: $5,980
    - 1+ children: $5,980

    Example: Joint filers with 2 children
    - Base phase-out start: $19,330
    - Joint bonus: $5,980
    - Actual phase-out start: $19,330 + $5,980 = $25,310
    """

    def formula(tax_unit, period, parameters):
        count_children = tax_unit("eitc_child_count", period)
        # Use FROZEN 2020 parameters per Oklahoma statute
        eitc = parameters("2020-01-01").gov.irs.credits.eitc
        is_joint = tax_unit("tax_unit_is_joint", period)
        # Joint filers get a higher phase-out start threshold
        joint_bonus = eitc.phase_out.joint_bonus.calc(count_children)
        phase_out_start = eitc.phase_out.start.calc(count_children)
        return phase_out_start + is_joint * joint_bonus
