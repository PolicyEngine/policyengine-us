"""
This file defines the entities needed by our legislation.

Taxes and benefits can be calculated for different entities: persons, household, companies, etc.

See https://openfisca.org/doc/key-concepts/person,_entities,_role.html
"""

from openfisca_core.entities import build_entity

TaxUnit = build_entity(
    key="taxunit",
    plural="taxunits",
    label="Tax Unit",
    doc="""
    A tax unit.
    """,
    roles=[
        dict(key="head", label="Head", max=1, doc="The head filer"),
        dict(
            key="spouse",
            label="Spouse",
            max=1,
            doc="The spouse if joint filing",
        ),
        dict(
            key="dependent",
            label="Dependent",
            doc="Dependents in the tax unit",
        ),
    ],
)

Household = build_entity(
    key="household",
    plural="households",
    label="Household",
    doc="""
    A household.
    """,
    roles=[
        dict(
            key="head",
            label="Head",
            max=1,
            doc="The reference person for the household",
        ),
        dict(
            key="non_head",
            label="Non-head",
            doc="Any person other than the head-of-household",
        ),
    ],
)

Family = build_entity(
    key="family",
    plural="families",
    label="Family",
    doc="""
    A family.
    """,
    roles=[
        dict(
            key="head",
            label="Head",
            max=1,
            doc="The reference person for the family",
        ),
        dict(
            key="spouse",
            label="Spouse",
            max=1,
            doc="The spouse if joint filing",
        ),
        dict(
            key="dependent",
            label="Dependent",
            doc="Dependents in the tax unit",
        ),
    ],
)

Person = build_entity(
    key="person",
    plural="people",
    label="Person",
    doc="""
    A person.
    """,
    is_person=True,
)

entities = [Household, TaxUnit, Family, Person]
