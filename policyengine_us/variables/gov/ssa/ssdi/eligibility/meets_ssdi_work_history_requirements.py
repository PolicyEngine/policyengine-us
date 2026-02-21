from policyengine_us.model_api import *


class meets_ssdi_work_history_requirements(Variable):
    value_type = bool
    entity = Person
    label = "Meets SSDI work history requirements"
    definition_period = YEAR
    reference = "https://www.ssa.gov/benefits/disability/qualify.html"
    documentation = """
    Determines if person meets the work history requirements for SSDI.
    Generally requires 40 credits total with 20 earned in the last 10 years.
    Younger workers may qualify with fewer credits.
    """

    def formula(person, period, parameters):
        p = parameters(period).gov.ssa.ssdi.work_credits

        total_credits = person("ssdi_work_credits", period)
        recent_credits = person("ssdi_recent_work_credits", period)
        age = person("age", period)

        # Access parameter trees
        duration = p.duration_of_work
        recent = p.recent_work

        # Standard requirement per 42 USC 423(c)(1)(B)(i)
        standard_requirement = (
            total_credits >= duration.standard_requirement
        ) & (recent_credits >= recent.standard_requirement)

        # Young worker exceptions per 42 USC 423(c)(1)(B)(ii)
        under_24 = duration.young_worker_requirements.under_24
        age_24_to_31 = duration.young_worker_requirements.age_24_to_31

        # Under 24: need specified credits in recent years
        under_24_exception = where(
            age < under_24.age_threshold,
            recent_credits >= under_24.credits_required,
            False,
        )

        # Age 24-31: credits = (age - base_age) * multiplier
        age_24_to_31_exception = where(
            (age >= under_24.age_threshold)
            & (age <= age_24_to_31.age_threshold),
            total_credits
            >= (age - age_24_to_31.base_age) * age_24_to_31.credits_multiplier,
            False,
        )

        young_worker_exception = under_24_exception | age_24_to_31_exception

        return standard_requirement | young_worker_exception
