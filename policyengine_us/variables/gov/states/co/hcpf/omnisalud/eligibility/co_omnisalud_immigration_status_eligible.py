from policyengine_us.model_api import *


class co_omnisalud_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Has eligible immigration status for Colorado OmniSalud"
    definition_period = YEAR
    defined_for = StateCode.CO
    reference = (
        "https://connectforhealthco.com/get-started/omnisalud/",
        "https://coloradoimmigrant.org/wp-content/uploads/2024/03/Eng.-OmniSalud-Guide-2024.pdf#page=1",
    )
    documentation = """
    Colorado OmniSalud covers immigrants who are NOT eligible for federal
    ACA subsidies due to their immigration status. This includes:
    - Undocumented immigrants (adults only starting 2025)
    - DACA recipients (before 2025 - they move to regular ACA in 2025)

    Starting 2025, undocumented children and pregnant individuals move to
    Health First Colorado (Medicaid).
    """

    def formula(person, period, parameters):
        p = parameters(period).gov.states.co.hcpf.omnisalud.eligibility
        immigration_status = person("immigration_status", period)
        age = person("age", period)
        is_pregnant = person("is_pregnant", period)

        # Check if undocumented
        undocumented = (
            immigration_status
            == immigration_status.possible_values.UNDOCUMENTED
        )

        # Check if DACA (covered before 2025)
        is_daca = immigration_status == immigration_status.possible_values.DACA

        # Children and pregnant individuals move to Health First Colorado in 2025
        is_child = age <= p.child_max_age

        # Determine if person's status is covered by OmniSalud
        # Undocumented adults are always covered
        # Undocumented children covered before 2025 (parameter controls this)
        # Undocumented pregnant covered before 2025
        # DACA covered before 2025 (parameter controls this)
        undocumented_child_covered = (
            undocumented & is_child & p.covers_undocumented_children
        )
        undocumented_pregnant_covered = (
            undocumented & is_pregnant & p.covers_undocumented_children
        )
        undocumented_adult_covered = undocumented & ~is_child & ~is_pregnant
        daca_covered = is_daca & p.covers_daca

        return (
            undocumented_adult_covered
            | undocumented_child_covered
            | undocumented_pregnant_covered
            | daca_covered
        )
