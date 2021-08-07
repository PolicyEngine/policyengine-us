from openfisca_core.entities import build_entity

TaxUnit = build_entity(
    key="tax_unit",
    plural="tax_units",
    label="Tax unit",
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

SPMUnit = build_entity(
    key="spm_unit",
    plural="spm_units",
    label="SPM unit",
    doc="""
    An SPM unit.
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

entities = [Household, SPMUnit, Family, TaxUnit, Person]
