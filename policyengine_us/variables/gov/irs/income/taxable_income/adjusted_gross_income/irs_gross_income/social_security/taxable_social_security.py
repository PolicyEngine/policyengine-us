from policyengine_us.model_api import *


def allocate_to_head_and_spouse(person, period, unit_amount, benefits, unit_benefits):
    """Split a tax unit amount between the head and spouse in proportion to
    their benefits. The spouse takes their share and the head the rest, so
    the two parts always sum to the tax unit amount."""
    # Use mask instead of where to avoid divide-by-zero warnings. Default to zero.
    person_frac = np.zeros_like(unit_benefits)
    mask = unit_benefits > 0
    person_frac[mask] = benefits[mask] / unit_benefits[mask]
    is_spouse = person("is_tax_unit_spouse", period)
    spouse_frac = min_(1, where(is_spouse, person_frac, 0))
    unit_spouse_frac = person.tax_unit.sum(spouse_frac)
    is_head = person("is_tax_unit_head", period)
    head_frac = where(is_head, 1 - unit_spouse_frac, 0)
    unit_head_frac = person.tax_unit.sum(head_frac)
    return unit_amount * select(
        [is_head, is_spouse], [unit_head_frac, unit_spouse_frac], default=0
    )


class taxable_social_security(Variable):
    value_type = float
    entity = Person
    label = "Taxable Social Security"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        unit_tss = person.tax_unit("tax_unit_taxable_social_security", period)
        # allocate unit_tss to head and spouse in proportion to social_security
        ind_socsec = person("social_security", period)
        unit_socsec = person.tax_unit("tax_unit_social_security_for_taxability", period)
        return allocate_to_head_and_spouse(
            person, period, unit_tss, ind_socsec, unit_socsec
        )
