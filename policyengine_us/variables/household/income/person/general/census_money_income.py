from policyengine_us.model_api import *


class census_money_income(Variable):
    value_type = float
    entity = Person
    label = "Census money income"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Money income as the Census Bureau reports it from the Current "
        "Population Survey: the sum of the 18 sources in Current Population "
        "Reports P60-200 (1998), Appendix A, which the survey's subject "
        "definitions still list, before taxes. Each source is a list in "
        "gov.household.census_money_income_sources. Retirement account "
        "distributions count from age 58, as in the survey since the "
        "redesigned processing system it introduced in 2019, which covers "
        "2018 income. It leaves out capital "
        "gains, discharged debt, tax refunds and credits, lump-sum insurance "
        "payments, and noncash benefits such as SNAP, school meals, housing "
        "assistance, child care subsidies and health coverage. A benefit the "
        "model computes for a group (an SPM unit, tax unit or household) is "
        "split equally among the group's members, as household totals split "
        "group amounts; the Current Population Survey records each payment "
        "for the person who reports it. The variable covers people of every "
        "age, while Census asks the income questions of people 15 and older "
        "and records SSI paid for a younger child in a parent's or guardian's "
        "SSI income. The model lacks three sources Appendix A lists: Black "
        "lung payments, military family allotments and foreign government "
        "pensions. It has foster child payments only for Los Angeles County, "
        "and no variable for interest credited inside retirement accounts, "
        "which the survey counts as interest: Appendix A lists IRAs among "
        "interest sources, and the survey's files give interest excluding "
        "retirement accounts as a separate amount (TRDINT_VAL)."
    )
    reference = (
        # PDF pages 1-3
        "https://www2.census.gov/programs-surveys/cps/methodology/Appendix%20A%20P60-200%20income%20measurement%20definition.pdf#page=1",
        "https://www.census.gov/programs-surveys/cps/technical-documentation/subject-definitions.html",
        # SSI received on behalf of a disabled or blind child (RESNSSI1 and
        # RESNSSI2, codes 3 and 4).
        "https://www2.census.gov/programs-surveys/cps/datasets/2026/march/asec2026_ddl_pub_full.pdf#page=51",
        # Interest excluding retirement account interest (TRDINT_VAL).
        "https://www2.census.gov/programs-surveys/cps/datasets/2026/march/asec2026_ddl_pub_full.pdf#page=57",
    )

    def formula(person, period, parameters):
        sources = parameters(period).gov.household.census_money_income_sources
        person_level = []
        group_level = []
        for item in sources:
            for name in sources[item]:
                entity = person.entity.get_variable(name).entity
                if entity.is_person:
                    person_level.append(name)
                else:
                    group_level.append((name, entity.key))
        total = add(person, period, person_level)
        for name, entity_key in group_level:
            group = person.simulation.populations[entity_key]
            total = total + group.project(group(name, period)) / group.project(
                group.nb_persons()
            )
        return total
