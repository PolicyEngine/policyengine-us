from policyengine_us.model_api import *


class rrc_cares_qualifying_children_with_valid_ssn(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    label = "Count of CTC qualifying children with valid SSN for CARES RRC"
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/6428#g_1_C",
        "https://www.law.cornell.edu/uscode/text/26/6428A#g_3",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_ctc_qualifying_child = person("ctc_qualifying_child", period)
        has_valid_ssn = person(
            "meets_eitc_identification_requirements", period
        )
        return tax_unit.sum(is_ctc_qualifying_child & has_valid_ssn)
