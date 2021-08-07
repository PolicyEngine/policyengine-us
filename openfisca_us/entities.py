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
        dict(
            key="member",
            label="Member",
            doc="A member of the group",
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
            key="member",
            label="Member",
            doc="A member of the group",
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
            key="member",
            label="Member",
            doc="A member of the group",
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
