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
        # long-term capital gains
        person_ltcg = person("long_term_capital_gains", period)
        tax_unit_ltcg = tax_unit.sum(person_ltcg)
        # Use mask to avoid divide-by-zero, default to zero allocation
        person_share = np.zeros_like(tax_unit_ltcg)
        mask = tax_unit_ltcg > 0
        person_share[mask] = person_ltcg[mask] / tax_unit_ltcg[mask]
        return person_share * tax_unit_subtraction
