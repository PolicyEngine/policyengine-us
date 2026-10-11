from policyengine_us.model_api import *


class part_d_lis_resource_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Resource eligible for the Medicare Part D low-income subsidy"
    documentation = (
        "Countable resources of the person and a spouse living with them do "
        "not exceed the individual or couple limit plus the burial funds "
        "exclusion for each of them."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1395w-114#a_3_E",
        "https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-423/subpart-P/section-423.773#p-423.773(d)(2)",
        "https://www.ecfr.gov/current/title-20/chapter-III/part-418/subpart-D/section-418.3410",
        "https://www.ecfr.gov/current/title-20/chapter-III/part-418/subpart-D/section-418.3425",
        "https://secure.ssa.gov/poms.nsf/lnx/0603030025",
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.hhs.medicare.part_d.low_income_subsidy.eligibility.resources
        resources = person.marital_unit.sum(add(person, period, p.sources))
        couple_size = person.marital_unit.nb_persons()
        limit = where(couple_size == 2, p.limit.couple, p.limit.individual)
        return resources <= limit + p.burial_exclusion * couple_size
