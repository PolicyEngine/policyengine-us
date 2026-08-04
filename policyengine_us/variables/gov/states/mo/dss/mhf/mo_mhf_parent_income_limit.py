from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class mo_mhf_parent_income_limit(Variable):
    value_type = float
    entity = Person
    label = "Missouri MHF parent income limit"
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.MO
    reference = (
        "https://dssmanuals.mo.gov/family-mo-healthnet-magi/1810-000-00/1810-020-00/1810-020-10/",
        "https://dssmanuals.mo.gov/family-mo-healthnet-magi/1805-000-00/1805-030-00/1805-030-20/1805-030-20-20/1805-030-20-20-05/",
        "https://web.archive.org/web/20210303084354/https://dssmanuals.mo.gov/wp-content/uploads/2019/03/MAGIappendix-a.pdf#page=1",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mo.dss.mhf.income_limit
        size = person("medicaid_household_size", period)
        capped_size = min_(size, p.max_household_size).astype(int)
        additional_people = max_(size - p.max_household_size, 0)

        monthly_limit = p.amount[capped_size] + additional_people * p.additional_person
        annual_limit = monthly_limit * MONTHS_IN_YEAR
        state_group = person.household("state_group_str", period)
        limit_ratio = annual_limit / fpg(size, state_group, period, parameters)
        # The conditional 5-point MAGI disregard in 1805.030.20.20.05 applies
        # only at the highest standard under which the person may qualify
        # (42 CFR 435.603(d)(4)). Since the adult expansion took effect
        # (July 1, 2021) that is the AEG, so the current schedule is the raw
        # ratio; before the expansion, Appendix A published a separate "MHF
        # Adult" row equal to this schedule plus 5% of the FPG, captured by
        # the dated fpl_disregard parameter.
        return limit_ratio + p.fpl_disregard
