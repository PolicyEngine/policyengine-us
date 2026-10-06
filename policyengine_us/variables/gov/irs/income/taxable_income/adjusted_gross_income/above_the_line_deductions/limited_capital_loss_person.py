from policyengine_us.model_api import *


class limited_capital_loss_person(Variable):
    value_type = float
    entity = Person
    label = "Limited capital loss deduction for each person"
    unit = USD
    documentation = (
        "Each head's or spouse's part of the tax unit's capital loss "
        "deduction after the Section 1211(b) limit (limited_capital_loss), in "
        "proportion to their own net capital losses. A tax unit dependent's "
        "capital losses are on their own return, so their part is zero."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/1211#b"

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        filer = ~person("is_tax_unit_dependent", period)
        filers = tax_unit.sum(filer)
        capital_loss = filer * person("capital_losses", period)
        total_capital_loss = tax_unit.sum(capital_loss)
        # When no member has a capital loss but the deduction was set
        # directly, the head and spouse share it equally.
        share = where(
            total_capital_loss > 0,
            np.divide(
                capital_loss,
                total_capital_loss,
                out=np.zeros_like(total_capital_loss, dtype=float),
                where=total_capital_loss > 0,
            ),
            np.divide(
                filer.astype(float),
                filers,
                out=np.zeros_like(filers, dtype=float),
                where=filers > 0,
            ),
        )
        return tax_unit("limited_capital_loss", period) * share
