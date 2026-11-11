from policyengine_us.model_api import *


def section_86_share(tax_unit, period, benefits_variable):
    """Share of the head's and spouse's section 86 benefits that one kind of
    benefit makes up. Section 86 figures a single taxable amount on title II
    and tier 1 railroad benefits together; each kind carries its share."""
    benefits = tax_unit(benefits_variable, period)
    total = tax_unit("tax_unit_section_86_benefits", period)
    share = np.zeros_like(total)
    mask = total > 0
    share[mask] = benefits[mask] / total[mask]
    return share


class tax_unit_taxable_social_security(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Taxable Social Security benefits"
    documentation = (
        "Title II Social Security (OASDI) benefits included in AGI: the title "
        "II share of tax_unit_taxable_section_86_benefits. Tier 1 railroad "
        "retirement benefits carry the rest, in "
        "tax_unit_taxable_railroad_social_security_equivalent_benefits."
    )
    unit = USD
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/86",
        "https://www.law.cornell.edu/uscode/text/26/86#d_1",
    )

    def formula(tax_unit, period, parameters):
        taxable = tax_unit("tax_unit_taxable_section_86_benefits", period)
        share = section_86_share(
            tax_unit, period, "tax_unit_social_security_for_taxability"
        )
        return taxable * share
