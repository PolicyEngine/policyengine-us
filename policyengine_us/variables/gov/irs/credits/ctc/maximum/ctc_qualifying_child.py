from policyengine_us.model_api import *


class ctc_qualifying_child(Variable):
    value_type = bool
    entity = Person
    label = "CTC-qualifying child"
    documentation = (
        "Child qualifies for the Child Tax Credit, including the filer "
        "identification requirements"
    )
    definition_period = YEAR
    defined_for = "is_tax_unit_dependent"
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/24#c",
        "https://www.law.cornell.edu/uscode/text/26/24#e_2",
        "https://www.law.cornell.edu/uscode/text/26/24#h_7",
        # 2025 Instructions for Schedule 8812, SSN Required Before the Due
        # Date of Your Return To Claim the CTC and ACTC.
        "https://www.irs.gov/pub/irs-prior/i1040s8--2025.pdf#page=1",
    )

    def formula(person, period, parameters):
        qualifying_child = person(
            "ctc_qualifying_child_ignoring_filer_identification", period
        )
        # IRC 24(h)(7)(A) allows no credit "with respect to any qualifying
        # child" unless the return includes the taxpayer's social security
        # number (on a joint return, at least one spouse's), and IRC 24(e)(2)
        # allows no credit if the taxpayer's identification number was issued
        # after the due date. A child whose filer fails these tests is not
        # counted. After a paragraph (7) denial, IRC 24(h)(4)(C) moves the
        # child to the credit for other dependents; a 24(e)(2) failure denies
        # that credit too (see ctc_adult_individual_maximum).
        filer_meets_identification_requirements = person.tax_unit(
            "filer_meets_child_ctc_identification_requirements", period
        )
        return qualifying_child & filer_meets_identification_requirements
