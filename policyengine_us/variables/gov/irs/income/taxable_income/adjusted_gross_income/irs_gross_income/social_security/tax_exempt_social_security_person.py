from policyengine_us.model_api import *


class tax_exempt_social_security_person(Variable):
    value_type = float
    entity = Person
    label = "Tax-exempt Social Security (person)"
    unit = USD
    documentation = (
        "The person's own Social Security benefits that section 86 leaves out "
        "of gross income on the return that reports them. For the head and "
        "spouse, that return is theirs, and taxable_social_security gives "
        "each their share of its taxable benefits. A tax unit dependent's "
        "benefits are taxed on the dependent's own return "
        "(dependent_taxable_social_security), not on the claimant's. Summed "
        "over the head and spouse, this is filer_tax_exempt_social_security."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/86",
        # IRS Pub. 915 (2025), "Who is taxed": one-half of a child's benefits
        # is added to the child's other income, not the parent's.
        "https://www.irs.gov/pub/irs-prior/p915--2025.pdf#page=5",
    )

    def formula(person, period, parameters):
        social_security = person("social_security", period)
        # Each is zero for the people the other covers.
        filer_taxable = person("taxable_social_security", period)
        dependent_taxable = person("dependent_taxable_social_security", period)
        return social_security - filer_taxable - dependent_taxable
