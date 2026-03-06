from policyengine_us.model_api import *


class rrc_qualifies_for_armed_forces_exception(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Tax unit qualifies for RRC Armed Forces SSN exception"
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/6428#g_4",
        "https://www.law.cornell.edu/uscode/text/26/6428A#g_5",
        "https://www.law.cornell.edu/uscode/text/26/6428B#e_2_E",
    )

    def formula(tax_unit, period, parameters):
        # Per 26 USC 6428(g)(4), 6428A(g)(5), and 6428B(e)(2)(E):
        # "at least 1 spouse was a member of the Armed Forces...
        # AND the valid identification number of at least 1 spouse is included"
        # These are TWO INDEPENDENT conditions - can be different people
        person = tax_unit.members
        is_joint = tax_unit("tax_unit_is_joint", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        is_military = person("is_military", period)
        has_valid_ssn = person("meets_eitc_identification_requirements", period)
        # Check conditions independently (can be different spouses)
        has_military_spouse = tax_unit.any(head_or_spouse & is_military)
        has_spouse_with_ssn = tax_unit.any(head_or_spouse & has_valid_ssn)
        return is_joint & has_military_spouse & has_spouse_with_ssn
