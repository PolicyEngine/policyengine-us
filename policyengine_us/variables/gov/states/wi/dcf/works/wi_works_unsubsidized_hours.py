from policyengine_us.model_api import *


class wi_works_unsubsidized_hours(Variable):
    value_type = float
    entity = SPMUnit
    label = "Wisconsin Works weekly hours of unsubsidized work"
    unit = "hour"
    definition_period = YEAR
    defined_for = StateCode.WI
    documentation = (
        "Usual weekly hours of the parent with the fewest hours, averaged over "
        "all weeks of the year. W-2 places one parent at a time, and the "
        "agency can place the parent who works less, so that parent's hours "
        "set the Community Service Job payment. Zero weeks worked means not "
        "reported and keeps usual hours."
    )
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/49/iii/148/1/b",
        "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/07/7.4.1_Community_Service_Jobs_(CSJ).htm",
        "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/14/14.2.1_W-2_Placements_for_Two-Parent_Households_at_Application.htm",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        usual_hours = person("weekly_hours_worked_before_lsr", period)
        weeks = person("weeks_worked", period)
        averaged_hours = usual_hours * min_(weeks, WEEKS_IN_YEAR) / WEEKS_IN_YEAR
        hours = where(weeks > 0, averaged_hours, usual_hours)
        is_parent = person("is_tax_unit_head_or_spouse", period)
        return spm_unit.min(where(is_parent, hours, np.inf))
