from policyengine_us.model_api import *


class rrc_arpa_dependents_with_valid_ssn(Variable):
    # Note: Unlike CARES (6428(g)(1)(C)) and CAA (6428A(g)(3)), ARPA
    # intentionally omits the filer-SSN precondition for dependents per
    # 26 USC 6428B(e)(2)(C). Dependents with SSN count even if no filer has SSN.
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    label = "Count of dependents with valid SSN for ARPA RRC"
    reference = "https://www.law.cornell.edu/uscode/text/26/6428B#e_2_C"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_dependent = person("is_tax_unit_dependent", period)
        has_valid_ssn = person("meets_eitc_identification_requirements", period)
        return tax_unit.sum(is_dependent & has_valid_ssn)
