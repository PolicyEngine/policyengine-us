from policyengine_us.model_api import *


class is_aca_filer(Variable):
    value_type = bool
    entity = Person
    label = "Filer or joint filer for ACA tax family calculations"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/26/1.36B-1#d"
    documentation = (
        "Keeps the tax unit's head and spouse, completing an absent or "
        "partial set with the oldest remaining members: one filer, or two "
        "on a joint return. Supplied tax-unit dependency hints exclude "
        "dependents from this fallback when possible. Ages alone cannot "
        "distinguish a filer from an equally old dependent; supply explicit "
        "head/spouse roles for such ambiguous households. This ACA-only "
        "inference has no adult-age cutoff and does not change the tax "
        "unit's other roles."
    )

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        filer = person("is_tax_unit_head_or_spouse", period)
        status = tax_unit("filing_status", period)
        joint = status == status.possible_values.JOINT
        missing_filers = max_(0, 1 + joint - tax_unit.sum(filer))
        candidate = ~filer
        # A calculated dependent array reflects the incomplete roles we are
        # filling in, so only supplied dependency hints can restrict candidates.
        if has_input_for_period(person.simulation, "is_tax_unit_dependent", period):
            dependent = person("is_tax_unit_dependent", period)
            candidate &= where(tax_unit.any(~dependent), ~dependent, True)
        rank = person.get_rank(tax_unit, -person("age", period), candidate)
        return filer | (candidate & (rank < missing_filers))
