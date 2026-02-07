from policyengine_us.model_api import *


class is_child_dependent(Variable):
    value_type = bool
    entity = Person
    label = "Is a child dependent based on the IRS definition"
    documentation = """
    A person qualifies as a child dependent if they are a tax unit dependent
    and meet any of the following criteria:
    1. Qualifying child: meets the age test (under 19, or under 24 if student)
       per IRC 152(c)(3)(A)
    2. Qualifying relative: fails age test but has gross income below threshold
       per IRC 152(d)
    3. Permanently disabled: exempt from age test per IRC 152(c)(3)(B)
    """
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/152#c_3_A",
        "https://www.law.cornell.edu/uscode/text/26/152#c_3_B",
        "https://www.law.cornell.edu/uscode/text/26/152#d",
    ]
    definition_period = YEAR
    defined_for = "is_tax_unit_dependent"

    def formula(person, period, parameters):
        # Three pathways to qualify as a child dependent:
        # 1. Qualifying child (meets age test)
        is_qualifying_child = person("is_qualifying_child_dependent", period)
        # 2. Qualifying relative (fails age test but meets income test)
        is_qualifying_relative = person(
            "is_qualifying_relative_dependent", period
        )
        # 3. Permanently disabled (exempt from age test)
        is_disabled = person("is_permanently_and_totally_disabled", period)
        return is_qualifying_child | is_qualifying_relative | is_disabled
