from policyengine_us.model_api import *


class rrc_adult_count_with_valid_ssn(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    label = "Count of tax unit head/spouse with valid SSN for RRC"
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/6428#g_1_A",
        "https://www.law.cornell.edu/uscode/text/26/6428#g_1_B",
        "https://www.law.cornell.edu/uscode/text/26/6428A#g_1",
        "https://www.law.cornell.edu/uscode/text/26/6428A#g_2",
        "https://www.law.cornell.edu/uscode/text/26/6428B#e_2_A",
        "https://www.law.cornell.edu/uscode/text/26/6428B#e_2_B",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # Reuse existing EITC SSN check - identical definition (SSN required)
        has_valid_ssn = person("meets_eitc_identification_requirements", period)
        return tax_unit.sum(head_or_spouse & has_valid_ssn)
