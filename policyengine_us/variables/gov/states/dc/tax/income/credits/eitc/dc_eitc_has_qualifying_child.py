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
    )
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        # Selects between the with-children schedule of (f)(1)(B)-(B-2) and
        # the childless schedule of (f)(1)(C). A child with an ITIN is a
        # qualifying child in every year: before 2023 IRC 32(c)(3)(D) only
        # keeps such a child out of the credit computation (see
        # dc_eitc_with_qualifying_child), and the unit still cannot use the
        # childless schedule.
        person = tax_unit.members
        qualifying_child = person("is_eitc_qualifying_child", period) & person(
            "has_tin", period
        )
        return tax_unit.any(qualifying_child)
