from policyengine_us.model_api import *


class wi_works_unsubsidized_hours(Variable):
    value_type = float
    entity = SPMUnit
    label = "Wisconsin Works weekly hours of unsubsidized work"
    unit = "hour"
    definition_period = MONTH
    defined_for = StateCode.WI
    documentation = (
        "Usual weekly hours of the custodial parent with the fewest hours, "
        "averaged over all weeks of the year. W-2 places one parent at a time, "
        "and the agency can place the parent who works less, so that parent's "
        "hours set the Community Service Job payment. Hours are annual inputs, "
        "so a parent who works part of the year reads as working fewer hours "
        "in every month. Zero weeks worked means not reported and keeps usual "
        "hours. Custodial parents who claim the child count first, because "
        "own_children_in_household also counts adult children. Other custodial "
        "parents come next, then whoever claims the child. A unit with none of "
        "these reads as zero hours."
    )
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/49/iii/148/1/b",
        "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/07/7.4.1_Community_Service_Jobs_(CSJ).htm",
        "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/14/14.2.1_W-2_Placements_for_Two-Parent_Households_at_Application.htm",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        usual_hours = person("weekly_hours_worked_before_lsr", period.this_year)
        weeks = person("weeks_worked", period.this_year)
        averaged_hours = usual_hours * min_(weeks, WEEKS_IN_YEAR) / WEEKS_IN_YEAR
        hours = where(weeks > 0, averaged_hours, usual_hours)
        custodial = person("wi_works_custodial_parent", period)
        dependent_child = person("is_person_demographic_tanf_eligible", period)
        claimant = person.tax_unit.any(dependent_child) & person(
            "is_tax_unit_head_or_spouse", period.this_year
        )
        custodial_claimant = custodial & claimant
        parents = select(
            [
                spm_unit.project(spm_unit.any(custodial_claimant)),
                spm_unit.project(spm_unit.any(custodial)),
            ],
            [custodial_claimant, custodial],
            default=claimant,
        )
        fewest_hours = spm_unit.min(where(parents, hours, np.inf))
        return where(np.isfinite(fewest_hours), fewest_hours, 0)
