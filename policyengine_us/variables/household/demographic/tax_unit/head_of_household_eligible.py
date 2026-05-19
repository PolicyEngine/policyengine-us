from policyengine_us.model_api import *


class head_of_household_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Qualifies for head of household filing status"
    reference = "https://www.law.cornell.edu/uscode/text/26/2#b"

    def formula(tax_unit, period, parameters):
        # tax_unit_married is true iff a spouse is present in this tax unit.
        # JOINT filers have the spouse in the same unit (married=true);
        # MFS filers have the spouse in a separate unit (married=false).
        # We use this signal to distinguish the IRC 7703(b) treated-unmarried
        # path (MFS, married=false) from a stray is_separated=true on a
        # JOINT filer (married=true), without reading filing_status and
        # creating a circular dependency through filing_status -> hoh_eligible.
        married = tax_unit("tax_unit_married", period)
        person = tax_unit.members
        # IRC 7703(b) "considered unmarried" applies to the taxpayer (head or
        # spouse), not to dependents. A separated dependent must not trigger
        # the 7703(b) child-only qualifying-person path.
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        is_separated = tax_unit.any(is_head_or_spouse & person("is_separated", period))
        # Qualifying children and permanently disabled always count
        is_qualifying_child = person("is_qualifying_child_dependent", period)
        is_disabled_dependent = person(
            "is_permanently_and_totally_disabled", period
        ) & person("is_tax_unit_dependent", period)
        # Qualifying relatives only count if related per IRC 2(b)(3)
        is_qualifying_relative = person("is_qualifying_relative_dependent", period)
        is_related = person("is_related_to_head_or_spouse", period)
        is_hoh_qualifying = (
            is_qualifying_child
            | is_disabled_dependent
            | (is_qualifying_relative & is_related)
        )
        has_qualifying_person = tax_unit.sum(is_hoh_qualifying) > 0
        # IRC 7703(b) treated-unmarried status supports HoH only through the
        # child-abode path, not the broader qualifying-relative route.
        # IRC 7703(b)(1) further requires the taxpayer to file a separate
        # return: a JOINT filer who is separated cannot claim HoH because
        # the joint return forecloses the "considered unmarried" path.
        treated_unmarried_qualifies = tax_unit.sum(is_qualifying_child) > 0
        surviving_spouse = tax_unit("surviving_spouse_eligible", period)
        unmarried_qualifies = has_qualifying_person & ~married & ~is_separated
        # ~married masks the JOINT-with-is_separated=true case: a JOINT
        # filer cannot use IRC 7703(b)(1) because they have not filed a
        # separate return. MFS filers (spouse in a different tax unit) have
        # married=false and continue to qualify via this branch.
        separated_qualifies = treated_unmarried_qualifies & is_separated & ~married
        return (unmarried_qualifies | separated_qualifies) & ~surviving_spouse
