from policyengine_us.model_api import *


class is_qualifying_relative_dependent(Variable):
    value_type = bool
    entity = Person
    label = "Is a qualifying relative dependent"
    documentation = """
    A qualifying relative is a dependent who does not meet the qualifying child
    age test but still qualifies as a dependent under IRC 152(d). Requirements:
    1. Relationship test (related to taxpayer or lives with them)
    2. Gross income below the threshold
    3. Support test (taxpayer provides over half of support - assumed)
    4. Not a qualifying child of anyone (per IRC 152(d)(1)(D))

    For head of household purposes, the person must also be related (not just
    living with the taxpayer) per IRC 2(b)(3).
    """
    definition_period = YEAR
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/152#d",
        "https://www.irs.gov/publications/p501",
    ]

    def formula(person, period, parameters):
        is_dependent = person("is_tax_unit_dependent", period)
        # Per IRC 152(d)(1)(D), cannot be a qualifying child of anyone.
        # This includes:
        # - Those who meet the age test (under 19, or under 24 if student)
        # - Those who are permanently disabled (exempt from age test per
        #   IRC 152(c)(3)(B))
        is_qualifying_child = person("is_qualifying_child_dependent", period)
        is_disabled = person("is_permanently_and_totally_disabled", period)
        not_qualifying_child = ~(is_qualifying_child | is_disabled)

        # Gross income must be below the exemption amount per IRC 152(d)(1)(B).
        # Although TCJA set the personal exemption to $0 from 2018, the gross
        # income limit continues at the 2017 level adjusted for inflation.
        gross_income = person("dependent_gross_income", period)
        p = parameters(period).gov.irs
        # Get 2017 exemption amount and apply uprating
        exemption_2017 = parameters(
            "2017-01-01"
        ).gov.irs.income.exemption.amount
        uprating_2017 = parameters("2017-01-01").gov.irs.uprating
        uprating_current = p.uprating
        income_limit = exemption_2017 * uprating_current / uprating_2017
        meets_income_test = gross_income < income_limit

        # For HOH purposes, must be related (not just living with taxpayer)
        is_related = person("is_related_to_head_or_spouse", period)

        return (
            is_dependent
            & not_qualifying_child
            & meets_income_test
            & is_related
        )
