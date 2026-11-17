from policyengine_us.model_api import *


class wi_veterans_property_tax_credit_retirement_income_exclusion_claimed(Variable):
    """A verified valid retirement exclusion is actually claimed on this return.

    This same-year legal fact is separate from the computed tax optimizer and
    its knowledge is included in facts_available. A true actual claim prohibits
    this veterans credit even if both raw elections are supplied. Do not force
    the derived retirement helper contrary to these source-qualified inputs;
    Core input overrides bypass formulas and are outside certified use here.
    """

    value_type = bool
    entity = TaxUnit
    label = "Wisconsin veterans credit claimant claims the retirement exclusion"
    definition_period = YEAR
    reference = "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/05/6/b/54m/d"
