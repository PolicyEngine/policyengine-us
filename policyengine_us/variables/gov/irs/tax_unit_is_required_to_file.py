from policyengine_us.model_api import *


class tax_unit_is_required_to_file(Variable):
    value_type = bool
    entity = TaxUnit
    label = "required to file federal taxes"
    documentation = """
    Whether this tax unit is legally required to file a federal income tax
    return under IRC § 6012, based on gross income thresholds and filing
    status.
    """
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/6012"

    def formula(tax_unit, period, parameters):
        gross_income = add(tax_unit, period, ["irs_gross_income"])
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
        unearned_income = gross_income - add(
            tax_unit, period, ["earned_income"]
        )
        unearned_income_over_threshold = (
            unearned_income > unearned_income_threshold
        )

        return income_over_exemption_amount | unearned_income_over_threshold
