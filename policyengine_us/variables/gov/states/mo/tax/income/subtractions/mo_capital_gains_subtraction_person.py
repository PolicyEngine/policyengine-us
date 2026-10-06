from policyengine_us.model_api import *


class mo_capital_gains_subtraction_person(Variable):
    value_type = float
    entity = Person
    label = "Missouri capital gains subtraction for each person"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revisor.mo.gov/main/OneSection.aspx?section=143.121&bid=57543",
        "https://dor.mo.gov/faq/taxation/individual/capital-gains-subtraction.html",
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        # Get the tax unit level capital gains subtraction
        tax_unit_subtraction = tax_unit("mo_capital_gains_subtraction", period)
        # The Department of Revenue enters the Form 1040 line 7a amount in the
        # Form MO-A column of the spouse with the gain. Allocate only across
        # the head and spouse with a positive gain of their own, capital gain
        # distributions included, so a spouse's capital loss does not
        # over-allocate the unit total. A tax unit dependent's gains are on
        # the dependent's own return and get no share.
        not_dependent = ~person("is_tax_unit_dependent", period)
        own_gains = person("capital_gains", period) + max_(
            0, person("non_sch_d_capital_gains", period)
        )
        person_positive_cg = not_dependent * max_(0, own_gains)
        tax_unit_positive_cg = tax_unit.sum(person_positive_cg)
        # If no head or spouse has a positive gain of their own (only possible
        # when the tax unit amount is supplied as an input), the head takes it.
        default_share = where(person("is_tax_unit_head", period), 1.0, 0.0)
        person_share = np.divide(
            person_positive_cg,
            tax_unit_positive_cg,
            out=default_share,
            where=tax_unit_positive_cg > 0,
        )
        return person_share * tax_unit_subtraction
