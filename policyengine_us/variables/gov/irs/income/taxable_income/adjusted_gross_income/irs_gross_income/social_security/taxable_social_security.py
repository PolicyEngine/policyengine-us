from policyengine_us.model_api import *


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
        unit_socsec = person.tax_unit("tax_unit_social_security", period)
        # Compute each person's share of tax unit's Social Security benefits.
        # Use mask instead of where to avoid divide-by-zero warnings. Default to zero.
        person_frac = np.zeros_like(unit_socsec)
        mask = unit_socsec > 0
        person_frac[mask] = ind_socsec[mask] / unit_socsec[mask]
        is_spouse = person("is_tax_unit_spouse", period)
        spouse_frac = min_(1, where(is_spouse, person_frac, 0))
        unit_spouse_frac = person.tax_unit.sum(spouse_frac)
        is_head = person("is_tax_unit_head", period)
        head_frac = where(is_head, 1 - unit_spouse_frac, 0)
        unit_head_frac = person.tax_unit.sum(head_frac)
        return unit_tss * select(
            [is_head, is_spouse], [unit_head_frac, unit_spouse_frac], default=0
        )
