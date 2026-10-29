from policyengine_us.model_api import *


class eitc_child_count(Variable):
    value_type = int
    entity = TaxUnit
    label = "EITC-qualifying children"
    unit = USD
    documentation = "Number of children qualifying as children for the EITC."
    definition_period = YEAR
    reference = (
        # IRC 32(c)(3)(D)(i) specifies qualifying children need a taxpayer identification number.
        "https://www.law.cornell.edu/uscode/text/26/32#c_3_D_i",
        # IRC 32(c)(3)(A) applies the IRC 152(c) qualifying-child definition.
        "https://www.law.cornell.edu/uscode/text/26/32#c_3_A",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_child = person("is_eitc_qualifying_child", period)
        identification_accepted = person("eitc_identification_accepted", period)
        eligible_child = is_child & identification_accepted
        # Only child who meets EITC identification requirements can claim benefit
        return tax_unit.sum(eligible_child)
