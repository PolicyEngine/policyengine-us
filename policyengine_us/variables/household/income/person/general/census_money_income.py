from policyengine_us.model_api import *


class census_money_income(Variable):
    value_type = float
    entity = Person
    label = "Census money income"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Money income as the Census Bureau defines it for its official income "
        "statistics: the sum of the 18 sources in Current Population Reports "
        "P60-200, Appendix A, before taxes. Each source is a list in "
        "gov.household.census_money_income_sources. It leaves out capital "
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
        "pensions."
    )
    reference = (
        # PDF pages 1-3
        "https://www2.census.gov/programs-surveys/cps/methodology/Appendix%20A%20P60-200%20income%20measurement%20definition.pdf#page=1",
        "https://cps.ipums.org/cps-action/variables/SSIKID",
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
