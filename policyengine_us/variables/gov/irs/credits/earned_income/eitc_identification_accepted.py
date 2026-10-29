from policyengine_us.model_api import *


class eitc_identification_accepted(Variable):
    value_type = bool
    entity = Person
    label = "Person's taxpayer identification number counts for the EITC"
    documentation = (
        "Whether the person meets the identification requirements the EITC "
        "variables apply: a Social Security number valid for employment "
        "(meets_eitc_identification_requirements), or, where a state credit "
        "waives 26 U.S.C. 32(m) (eitc_ssn_limitation_waived), any taxpayer "
        "identification number."
    )
    definition_period = YEAR
    reference = (
        # IRC 32(c)(1)(E) requires the filer's and spouse's taxpayer
        # identification numbers and 32(c)(3)(D) each qualifying child's.
        "https://www.law.cornell.edu/uscode/text/26/32#c_1_E",
        "https://www.law.cornell.edu/uscode/text/26/32#c_3_D",
        # IRC 32(m) limits that number to a Social Security number valid for
        # employment.
        "https://www.law.cornell.edu/uscode/text/26/32#m",
    )

    def formula(person, period, parameters):
        valid_ssn = person("meets_eitc_identification_requirements", period)
        waived = person.tax_unit("eitc_ssn_limitation_waived", period)
        return valid_ssn | (waived & person("has_tin", period))
