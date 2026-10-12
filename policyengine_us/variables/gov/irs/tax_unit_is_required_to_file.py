from policyengine_us.model_api import *
from policyengine_us.tools.section_911 import section_911_gross_exclusion


class tax_unit_is_required_to_file(Variable):
    value_type = bool
    entity = TaxUnit
    label = "required to file federal taxes"
    documentation = """
    Whether this tax unit is legally required to file a federal income tax
    return under IRC § 6012, based on gross income thresholds and filing
    status. Under § 6012(c), gross income includes amounts excluded under
    § 911: Form 2555 line 43 when Form 2555 leaf inputs are supplied,
    otherwise the legacy foreign_earned_income_exclusion amount.
    """
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/6012",
        # Gross income counts amounts excluded under section 911.
        "https://www.law.cornell.edu/uscode/text/26/6012#c",
        # Chart A: gross income includes income from sources outside the
        # United States "even if you can exclude part or all of it".
        "https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf#page=9",
        # Form 2555 line 43: the line 36 and line 42 exclusions.
        "https://www.irs.gov/pub/irs-prior/f2555--2025.pdf#page=3",
    )

    def formula(tax_unit, period, parameters):
        # Section 6012(c): for the filing requirement, gross income is
        # computed without regard to the section 911 exclusion. That is the
        # gross exclusion on Form 2555 line 43, not the worksheet line 2c
        # stacking amount, which is net of line 44 and worksheet line 2b and
        # includes the line 50 housing deduction.
        section_911_exclusion = section_911_gross_exclusion(tax_unit, period)
        gross_income = add(tax_unit, period, ["irs_gross_income"]) + (
            section_911_exclusion
        )
        p = parameters(period).gov.irs.income.exemption
        exemption_amount = 0 if p.suspended else p.amount

        # (a)(1)(A), (a)(1)(B)
        filing_status = tax_unit("filing_status", period).decode_to_str()
        separate = filing_status == "SEPARATE"
        standard_deduction = tax_unit("standard_deduction", period)
        threshold = where(
            separate,
            exemption_amount,
            standard_deduction + exemption_amount,
        )

        income_over_exemption_amount = gross_income > threshold

        # (a)(1)(C) - unearned income threshold for dependents
        unearned_income_threshold = 500 + tax_unit(
            "additional_standard_deduction", period
        )
        # The section 911 exclusion covers earned income only.
        unearned_income = (
            gross_income
            - add(tax_unit, period, ["earned_income"])
            - section_911_exclusion
        )
        unearned_income_over_threshold = unearned_income > unearned_income_threshold

        return income_over_exemption_amount | unearned_income_over_threshold
