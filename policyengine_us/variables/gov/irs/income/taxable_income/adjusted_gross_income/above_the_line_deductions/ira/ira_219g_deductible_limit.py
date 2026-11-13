from policyengine_us.model_api import *


class ira_219g_deductible_limit(Variable):
    value_type = float
    entity = Person
    label = "IRA dollar deduction limit after the employer-plan phase-out"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/219#g",
        "https://www.irs.gov/publications/p590a",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.ald.ira.phase_out
        retirement = parameters(period).gov.irs.gross_income.retirement_contributions
        catch_up = person("age", period) >= retirement.catch_up.age_threshold
        dollar_limit = retirement.limit.ira + catch_up * retirement.catch_up.limit.ira
        tax_unit = person.tax_unit
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        joint = filing_status == status.JOINT
        separate = filing_status == status.SEPARATE
        lived_together = separate & tax_unit("cohabitating_spouses", period)
        # Section 219(g)(4): separate filers living apart all year are unmarried
        # for this phase-out, so the spouse's coverage is disregarded.
        treated_as_single = separate & ~lived_together
        active = person("ira_active_participant", period)
        # A marital unit can span two separate tax units.
        spouse_active = person.marital_unit.sum(active) > active.astype(int)
        # Also support joint returns whose members omit explicit marital units.
        filer = person("is_tax_unit_head_or_spouse", period)
        other_joint_active = tax_unit.sum(active * filer) > (active & filer).astype(int)
        spouse_route = ~active & (
            (joint & other_joint_active) | (lived_together & spouse_active)
        )
        start = where(
            treated_as_single,
            p.start.SINGLE,
            where(spouse_route & joint, p.spouse_start, p.start[filing_status]),
        )
        width = where(
            treated_as_single,
            p.width.SINGLE,
            where(spouse_route & joint, p.spouse_width, p.width[filing_status]),
        )
        magi = tax_unit("ira_219g_magi", period).astype(np.float64)
        fraction = clip((magi - start) / width, 0, 1)
        # Section 219(g)(2)(C) rounds the reduction down to a multiple of $10.
        # Float32 income inputs can land infinitesimally below an exact multiple.
        reduction = (
            np.floor(np.round(dollar_limit * fraction, 6) / p.rounding_interval)
            * p.rounding_interval
        )
        phased_limit = where(
            magi >= start + width,
            0,
            max_(p.minimum, dollar_limit - reduction),
        )
        return where(active | spouse_route, phased_limit, dollar_limit)
