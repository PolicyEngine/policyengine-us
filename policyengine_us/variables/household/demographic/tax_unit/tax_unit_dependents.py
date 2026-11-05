from policyengine_us.model_api import *


class tax_unit_dependents(Variable):
    value_type = int
    entity = TaxUnit
    label = "Number of dependents in the tax unit"
    definition_period = YEAR
    documentation = (
        "The number of members with is_tax_unit_dependent set or inferred as true. "
        "Tax-unit membership alone does not establish dependency. Without explicit "
        "roles, a member aged 18 or older can be inferred as the spouse. Supplying "
        "filing_status alone, including SINGLE or HEAD_OF_HOUSEHOLD, does not prevent "
        "spouse inference. Supply is_tax_unit_dependent for the dependent, or provide "
        "complete tax_unit_role_input roles for every tax-unit member."
    )

    adds = ["is_tax_unit_dependent"]
