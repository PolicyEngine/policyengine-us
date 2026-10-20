from policyengine_us.model_api import *
from policyengine_us.tools.section_911 import elects_section_911_exclusion


class eitc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for EITC"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/32#c_1_A",
        # No EITC for an individual who claims the benefits of section 911.
        "https://www.law.cornell.edu/uscode/text/26/32#c_1_C",
        # Former section 32(c)(1)(F), struck from 2021.
        "https://www.govinfo.gov/content/pkg/USCODE-2015-title26/html/USCODE-2015-title26-subtitleA-chap1-subchapA-partIV-subpartC-sec32.htm",
    )

    def formula(tax_unit, period, parameters):
        eitc = parameters.gov.irs.credits.eitc(period)
        investment_income_eligible = tax_unit("eitc_investment_income_eligible", period)
        demographic_eligible = tax_unit("eitc_demographic_eligible", period)
        # The head or spouse in the tax unit must have valid SSN card type to be eligible for the EITC
        filers_has_ssn = tax_unit(
            "filer_meets_eitc_identification_requirements", period
        )
        # Section 32(c)(1)(C): "eligible individual" does not include an
        # individual who claims the benefits of section 911 (Form 2555).
        claims_section_911 = elects_section_911_exclusion(tax_unit, period)
        # Define eligibility before considering separate filer limitation.
        eligible = (
            demographic_eligible
            & investment_income_eligible
            & filers_has_ssn
            & ~claims_section_911
        )
        # Former section 32(c)(1)(F), through 2020: "No credit shall be
        # allowed under this section to any eligible individual who has one or
        # more qualifying children if no qualifying child of such individual
        # is taken into account under subsection (b) by reason of paragraph
        # (3)(D)", the identification requirement. The 2018-2020 Form 1040
        # instructions instead send such a filer to the credit without a
        # qualifying child; the model follows the statute.
        if eitc.eligibility.qualifying_child_without_identification_bar:
            person = tax_unit.members
            has_qualifying_child = tax_unit.any(
                person("is_eitc_qualifying_child", period)
            )
            no_child_counted = tax_unit("eitc_child_count", period) == 0
            eligible = eligible & ~(has_qualifying_child & no_child_counted)
        # This parameter is true if separate filers are eligible.
        if eitc.eligibility.separate_filer:
            return eligible
        # If separate filers are not eligible, check if the filer is separate.
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        return eligible & ~separate
