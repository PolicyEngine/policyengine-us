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
        # IRC 32(c)(3)(D) keeps a child without a Social Security number out
        # of the credit computation without making it a non-qualifying child.
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
        # the childless schedule of (f)(1)(C). A qualifying child with an ITIN
        # keeps the unit on the with-children schedule in every year; before
        # 2023 IRC 32(c)(3)(D) only leaves it out of the credit computation
        # (see dc_eitc_with_qualifying_child). A filer whose qualifying
        # children have neither a Social Security number nor an ITIN claims
        # the childless schedule: Line 27a says so from 2023, and
        # qualifying_child_tin_required applies the same treatment to earlier
        # years. Setting it to false keeps such a child a qualifying child.
        person = tax_unit.members
        p = parameters(period).gov.states.dc.tax.income.credits.eitc
        meets_identification = where(
            p.qualifying_child_tin_required, person("has_tin", period), True
        )
        qualifying_child = (
            person("is_eitc_qualifying_child", period) & meets_identification
        )
        return tax_unit.any(qualifying_child)
