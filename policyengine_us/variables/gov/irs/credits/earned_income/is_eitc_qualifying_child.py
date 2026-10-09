from policyengine_us.model_api import *


class is_eitc_qualifying_child(Variable):
    value_type = bool
    entity = Person
    label = "Is an EITC qualifying child before the identification requirement"
    documentation = """
    Whether a tax unit dependent is a qualifying child under IRC 32(c)(3)(A),
    which applies the IRC 152(c) qualifying-child definition. The taxpayer
    identification number requirement of IRC 32(c)(3)(D) is applied by each
    credit, because some states accept an ITIN where the federal credit
    requires a Social Security number.
    """
    definition_period = YEAR
    reference = (
        # IRC 32(c)(3)(A) applies the IRC 152(c) qualifying-child definition.
        "https://www.law.cornell.edu/uscode/text/26/32#c_3_A",
        # IRC 152(c)(2) is the relationship test.
        "https://www.law.cornell.edu/uscode/text/26/152#c_2",
        # IRC 152(c)(3)(B) waives the age test for permanently and totally disabled individuals.
        "https://www.law.cornell.edu/uscode/text/26/152#c_3_B",
    )

    def formula(person, period, parameters):
        # IRC 152(c)(3)(B) treats the age test of 152(c)(3)(A) as met for a
        # permanently and totally disabled dependent of any age.
        is_disabled_dependent = person("is_tax_unit_dependent", period) & person(
            "is_permanently_and_totally_disabled", period
        )
        meets_age_test = (
            person("is_qualifying_child_dependent", period) | is_disabled_dependent
        )
        # The waiver does not reach the IRC 152(c)(2) relationship test, which
        # admits only the taxpayer's children, siblings and their descendants.
        # A parent or grandparent fails it and can be a qualifying relative
        # (IRC 152(d)(2)(C)-(D)) but not a qualifying child. Other relatives
        # outside 152(c)(2) are not recorded, so they are not excluded here.
        fails_relationship_test = person(
            "is_parent_of_filer_or_spouse", period
        ) | person("is_grandparent_of_filer_or_spouse", period)
        return meets_age_test & ~fails_relationship_test
