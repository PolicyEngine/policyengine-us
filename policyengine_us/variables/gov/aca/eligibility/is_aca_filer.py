from policyengine_us.model_api import *


class is_aca_filer(Variable):
    value_type = bool
    entity = Person
    label = "Filer or joint filer for ACA tax family calculations"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/26/1.36B-1#d"
    documentation = (
        "Uses the tax unit's head and spouse when either role exists. When "
        "adult role inference leaves both absent, the oldest member files, "
        "or the two oldest on a joint return. Supplied tax-unit dependency "
        "hints exclude dependents from this fallback when possible. Ages "
        "alone cannot distinguish a filer from an equally old dependent; "
        "supply explicit head/spouse roles for such ambiguous households. "
        "This ACA-only inference does not change the tax unit's other roles."
    )

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        filer = person("is_tax_unit_head_or_spouse", period)
        has_filer = tax_unit.any(filer)
        # Read the stored hint without deriving dependency from the roles we
        # are filling in. If every member is marked dependent (including a
        # cached role-derived array for minors), retain the age fallback.
        dependent = person.simulation.get_array("is_tax_unit_dependent", period)
        candidate = person.filled_array(True)
        if dependent is not None:
            candidate = where(tax_unit.any(~dependent), ~dependent, candidate)
        rank = person.get_rank(tax_unit, -person("age", period), candidate)
        status = tax_unit("filing_status", period)
        joint = status == status.possible_values.JOINT
        inferred = candidate & (rank < (1 + joint))
        return where(has_filer, filer, inferred)
