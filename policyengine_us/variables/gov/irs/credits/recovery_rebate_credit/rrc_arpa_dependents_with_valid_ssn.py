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
        # IRC 6428B(b)(2) counts "the number of dependents of the taxpayer", and
        # under 152(b)(1) a return on which the filer (or, if joint, either
        # spouse) can be claimed as a dependent has none.
        dependent_filer = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
        )
        is_dependent = person("is_tax_unit_dependent", period) & ~dependent_filer
        has_valid_ssn = person("meets_eitc_identification_requirements", period)
        return tax_unit.sum(is_dependent & has_valid_ssn)
