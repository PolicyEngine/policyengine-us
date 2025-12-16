from policyengine_us.model_api import *


class mo_capital_gains_subtraction_person(Variable):
    value_type = float
    entity = Person
    label = "Missouri capital gains subtraction for each person"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/faq/taxation/individual/capital-gains-subtraction.html",
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        # Get the tax unit level capital gains subtraction
        tax_unit_subtraction = tax_unit("mo_capital_gains_subtraction", period)
        # Allocate proportionally based on each person's share of
        # capital gains (both short-term and long-term) to match
        # the net_capital_gain used at the tax unit level
        person_cg = person("capital_gains", period)
        tax_unit_cg = tax_unit.sum(person_cg)
        # Use mask to avoid divide-by-zero, default to zero allocation
        person_share = np.zeros_like(tax_unit_cg)
        mask = tax_unit_cg > 0
        person_share[mask] = person_cg[mask] / tax_unit_cg[mask]
        return person_share * tax_unit_subtraction
