from policyengine_us.model_api import *


class taxable_dependent_care_benefits(Variable):
    value_type = float
    entity = Person
    label = "Taxable dependent care benefits"
    documentation = (
        "Employer dependent care benefits above the IRC 129 exclusion (Form "
        "2441 line 26, reported on Form 1040 line 1e). Box 1 wages leave out "
        "all of dependent_care_employer_benefits, so this adds back the part "
        "the filer cannot exclude. The tax unit's amount is split among its "
        "members in proportion to their benefits."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        # IRC 129(a)(1) (the exclusion) and 129(a)(2)(B) (the excess is
        # gross income).
        "https://www.law.cornell.edu/uscode/text/26/129#a",
        # Form 2441 Part III, line 26: taxable benefits, to Form 1040 line 1e.
        "https://www.irs.gov/pub/irs-prior/f2441--2025.pdf#page=2",
    )

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        benefits = person("dependent_care_employer_benefits", period)
        # The tax_unit projector returns each member's unit-level value.
        unit_benefits = tax_unit.sum(benefits)
        exclusion = tax_unit("dependent_care_assistance_exclusion", period)
        unit_taxable = max_(unit_benefits - exclusion, 0)
        share = np.divide(
            benefits,
            unit_benefits,
            out=np.zeros_like(benefits),
            where=unit_benefits > 0,
        )
        return unit_taxable * share
