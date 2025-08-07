from policyengine_us.model_api import *


class meets_eitc_identification_requirements(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Person meets EITC identification requirements"
    reference = (
        # IRC 32(c)(1)(E) specifies filer and spouse needs a taxpayer identification number.
        "https://www.law.cornell.edu/uscode/text/26/32#c_1_E",
        # IRC 32(c)(3)(D)(i) specifies qualifying children need a taxpayer identification number.
        "https://www.law.cornell.edu/uscode/text/26/32#c_3_D_i",
        # IRC 32(m) defines a taxpayer identification number as a SSN,
        # except for those listed in sections II and III of SSA 205(c)(2)(B)(i).
        "https://www.law.cornell.edu/uscode/text/26/32#m",
        # SSA 205(c)(2)(B)(i) defines SSNs used for benefits.
        "https://www.ssa.gov/OP_Home/ssact/title02/0205.htm",
    )

    def formula(person, period, parameters):
        ssn_card_type = person("ssn_card_type", period)
        ssn_card_types = ssn_card_type.possible_values
        citizen = ssn_card_type == ssn_card_types.CITIZEN
        non_citizen_valid_ead = (
            ssn_card_type == ssn_card_types.NON_CITIZEN_VALID_EAD
        )
        return citizen | non_citizen_valid_ead
