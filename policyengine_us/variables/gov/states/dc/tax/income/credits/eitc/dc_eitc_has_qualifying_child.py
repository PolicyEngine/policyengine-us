from policyengine_us.model_api import *


class dc_eitc_has_qualifying_child(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Has a qualifying child for the DC EITC"
    definition_period = YEAR
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.04#(f)(1)",
        # (f)(4) gives "qualifying child" its IRC 32 meaning.
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.04#(f)(4)",
        # IRC 32(c)(3)(D) keeps a child without a Social Security number out of
        # the credit computation without making it a non-qualifying child.
        "https://www.law.cornell.edu/uscode/text/26/32#c_3_D",
        # From 2023, Line 27a: "Each qualifying child must have a valid social
        # security number (SSN) or individual taxpayer identification number
        # (ITIN) issued by the IRS. If you have no children who qualify, you
        # must claim the DC EITC without qualifying children."
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2023_D40_Book_Final_012324.pdf#page=18",
    )
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        # Selects between the with-children schedule of (f)(1)(B)-(B-2) and
        # the childless schedule of (f)(1)(C). Before 2023 identification plays
        # no part: a child with an ITIN or with no number at all is still a
        # qualifying child, since IRC 32(c)(3)(D) only keeps it out of the
        # credit computation (see dc_eitc_with_qualifying_child) and IRC 32(m)
        # treats the two alike, so the unit cannot use the childless schedule.
        # From 2023 the D-40 instructions require a Social Security number or
        # ITIN for each qualifying child claimed, and send a filer whose
        # children have neither to the childless schedule.
        person = tax_unit.members
        p = parameters(period).gov.states.dc.tax.income.credits.eitc
        meets_identification = where(
            p.qualifying_child_tin_required, person("has_tin", period), True
        )
        qualifying_child = (
            person("is_eitc_qualifying_child", period) & meets_identification
        )
        return tax_unit.any(qualifying_child)
