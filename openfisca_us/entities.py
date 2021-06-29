"""
This file defines the entities needed by our legislation.

Taxes and benefits can be calculated for different entities: persons, household, companies, etc.

See https://openfisca.org/doc/key-concepts/person,_entities,_role.html
"""

from openfisca_core.entities import build_entity

TaxUnit = build_entity(
    key="taxunit",
    plural="taxunits",
    label="The tax unit",
    doc="""
    Description of a tax unit
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

Person = build_entity(
    key="person",
    plural="people",
    label="An individual person",
    doc="""
    Description of a person
    """,
    is_person=True,
)

entities = [TaxUnit, Person]
