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
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_child = person("is_child_dependent", period)
        meets_eitc_identification_requirements = person(
            "meets_eitc_identification_requirements", period
        )
        eligible_child = is_child & meets_eitc_identification_requirements
        # Only child who meets EITC identification requirements can claim benefit
        return tax_unit.sum(eligible_child)
