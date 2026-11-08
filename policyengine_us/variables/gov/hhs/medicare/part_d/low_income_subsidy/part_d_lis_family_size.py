from policyengine_us.model_api import *


class part_d_lis_family_size(Variable):
    value_type = int
    entity = Person
    label = "Medicare Part D low-income subsidy family size"
    documentation = (
        "The person, a spouse living with them, and relatives living with "
        "them who depend on the person or spouse for at least half of their "
        "support, approximated by the dependents on the couple's tax "
        "returns: a joint return's dependents count once, and when the "
        "spouses file separately, the dependents on both returns count."
    )
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-423/subpart-P/section-423.772",
        "https://secure.ssa.gov/poms.nsf/lnx/0603020055",
    )

    def formula(person, period, parameters):
        couple_size = person.marital_unit.nb_persons()
        # Each tax unit's dependents count once, through the unit's head: on a
        # joint return the couple has one head, and spouses who file
        # separately each head their own return.
        head = person("is_tax_unit_head", period)
        dependents = person.tax_unit("tax_unit_dependents", period)
        return couple_size + person.marital_unit.sum(where(head, dependents, 0))
