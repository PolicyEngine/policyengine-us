from policyengine_us.model_api import *


def create_cdcc_single_parent_work_requirement() -> Reform:
    """
    Reform that changes CDCTC eligibility to require at least one parent to work
    instead of both parents.

    Current law: For married couples, childcare expenses are capped at the
    minimum of the two spouses' earnings, effectively requiring both to work.

    This reform: Changes the cap to the maximum of the two spouses' earnings,
    allowing families to qualify if at least one parent works.
    """

    class min_head_spouse_earned(Variable):
        value_type = float
        entity = TaxUnit
        label = "Greater of head and spouse's earnings (reform)"
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            is_joint = tax_unit("tax_unit_is_joint", period)
            head_earnings = tax_unit("head_earned", period)
            spouse_earnings = tax_unit("spouse_earned", period)
            # Use max_ instead of min_ to allow eligibility if at least
            # one parent works
            return where(
                is_joint, max_(head_earnings, spouse_earnings), head_earnings
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(min_head_spouse_earned)

    return reform


def create_cdcc_single_parent_work_requirement_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_cdcc_single_parent_work_requirement()

    # This reform can be controlled by a parameter if needed
    # For now, always return None unless bypassed
    return None


cdcc_single_parent_work_requirement = (
    create_cdcc_single_parent_work_requirement_reform(None, None, bypass=True)
)
