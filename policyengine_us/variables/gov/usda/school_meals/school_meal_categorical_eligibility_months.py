from policyengine_us.model_api import *


class school_meal_categorical_eligibility_months(Variable):
    value_type = int
    entity = SPMUnit
    label = "Months of the year school meal categorical eligibility covers"
    unit = "month"
    definition_period = YEAR
    documentation = (
        "Months of the year that categorical eligibility for free school "
        "meals covers, or zero without it. Twelve, unless every program that "
        "gives the unit categorical eligibility starts after January in the "
        "model's monthly values: SNAP and reported SNAP or TANF receipt by "
        "month, and Head Start eligibility by head_start_qualifying_months. "
        "Then it counts the months from the first month of participation "
        "through December. Eligibility from direct certification or an "
        "application lasts the rest of the school year and up to 30 operating "
        "days into the next, and the model carries it through December, so "
        "later months count even if participation stops. The model holds no "
        "earlier "
        "years, so it treats the first month of participation in the year "
        "as the household's first. Programs the model computes by year, such "
        "as TANF and FDPIR, cover the whole year."
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/245.6#c_1",
        "https://www.law.cornell.edu/cfr/text/7/245.2",
    )

    def formula(spm_unit, period, parameters):
        programs = parameters(period).gov.usda.school_meals.categorical_eligibility
        # Head Start eligibility is a yearly flag, so its months come from
        # head_start_qualifying_months below.
        other_programs = [
            program for program in programs if program != "is_head_start_eligible"
        ]
        # A program the model computes by year reads as one twelfth of its
        # yearly value in each month, so it counts from January.
        participating_yet = False
        months = 0
        for month in period.get_subperiods(MONTH):
            participating = add(spm_unit, month, other_programs) > 0
            participating_yet = participating_yet | participating
            months = months + participating_yet
        if "is_head_start_eligible" in programs:
            person = spm_unit.members
            head_start_months = where(
                person("is_head_start_eligible", period),
                person("head_start_qualifying_months", period),
                0,
            )
            months = max_(months, spm_unit.max(head_start_months))
        categorical = spm_unit("meets_school_meal_categorical_eligibility", period)
        # Categorical eligibility that no program places in a month, such as
        # eligibility given as an input, covers the whole year.
        return where(
            categorical,
            where(months > 0, months, MONTHS_IN_YEAR),
            0,
        )
