from policyengine_us.model_api import *
from policyengine_us.variables.household.income.person.dependent_care_employer_benefits import (
    form_2441_line_15,
)


class taxable_dependent_care_benefits(Variable):
    value_type = float
    entity = Person
    label = "Taxable dependent care benefits"
    documentation = (
        "Employer dependent care benefits above the IRC 129 exclusion (Form "
        "2441 line 26, reported on Form 1040 line 1e from 2022). Box 1 wages "
        "leave out all of dependent_care_employer_benefits, so this adds back "
        "the part the filer received and cannot exclude: Form 2441 line 15 "
        "(line 12 benefits less amounts forfeited or carried forward) less "
        "the exclusion. The tax unit's amount is split among its members in "
        "proportion to their line 15 amounts. A person's supplied "
        "taxable_dependent_care_benefits_reported of zero or more replaces "
        "their computed share; the exclusion and the child and dependent "
        "care credit stay computed, though the credit's rate follows "
        "adjusted gross income, which includes this amount. Supply "
        "taxable_dependent_care_benefits_reported rather than setting this "
        "variable: an input here replaces the formula for every person in "
        "the simulation that year, and people without a value get zero."
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
        # Each person's part of Form 2441 line 15: line 12 benefits less
        # amounts forfeited or carried forward (line 14).
        benefits = form_2441_line_15(person, period)
        # The tax_unit projector returns each member's unit-level value.
        unit_benefits = tax_unit.sum(benefits)
        exclusion = tax_unit("dependent_care_assistance_exclusion", period)
        # Line 26: line 15 less the line 25 exclusion. Line 22 (benefits from
        # the filer's own business) is zero for employee benefits.
        unit_taxable = max_(unit_benefits - exclusion, 0)
        share = np.divide(
            benefits,
            unit_benefits,
            out=np.zeros_like(benefits),
            where=unit_benefits > 0,
        )
        # A supplied line 26 amount of zero or more replaces this person's
        # computed share; a negative amount, such as the default -1, means
        # not supplied.
        reported = person("taxable_dependent_care_benefits_reported", period)
        return where(reported >= 0, reported, unit_taxable * share)
