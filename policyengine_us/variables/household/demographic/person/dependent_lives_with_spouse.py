from policyengine_us.model_api import *


class dependent_lives_with_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Dependent lives with their spouse"
    documentation = """
    Whether a dependent is married and lives with their spouse, read from the
    dependent's own marital unit (an unmarried person, or a married and
    co-habiting couple) rather than from the claimant's filing status. A
    dependent does not file a joint return (IRC 152(b)(2)), so a dependent
    who lives with their spouse has zero IRC 86(c) base amounts and files
    separately for the IRC 1211(b) capital loss limit.
    """
    definition_period = YEAR
    defined_for = "is_tax_unit_dependent"
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/86#c_1_C",
        "https://www.law.cornell.edu/uscode/text/26/152#b_2",
        "https://www.law.cornell.edu/uscode/text/26/152#d_2_H",
        "https://www.law.cornell.edu/uscode/text/26/7703#a",
    )

    def formula(person, period, parameters):
        in_couple = person.marital_unit.nb_persons() == 2
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        partner_is_head_or_spouse = spouse(person, period, "is_tax_unit_head_or_spouse")
        # A taxpayer's spouse is never the taxpayer's dependent
        # (IRC 152(d)(2)(H)). A marital unit that pairs a dependent with the
        # head or spouse of the dependent's own tax unit is the single default
        # unit created when a situation lists no marital units, not a marriage.
        filer_paired_with_dependent = (
            in_couple & head_or_spouse & ~partner_is_head_or_spouse
        )
        paired_with_own_filer = partner_is_head_or_spouse & person.tax_unit.any(
            filer_paired_with_dependent
        )
        # An individual legally separated under a decree of divorce or of
        # separate maintenance is not married (IRC 7703(a)(2)).
        is_separated = person("is_separated", period)
        return in_couple & ~paired_with_own_filer & ~is_separated
