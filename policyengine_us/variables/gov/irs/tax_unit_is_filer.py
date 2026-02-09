from policyengine_us.model_api import *


class tax_unit_is_filer(Variable):
    value_type = bool
    entity = TaxUnit
    label = "files taxes"
    documentation = """
    Whether this tax unit files a federal income tax return.

    A tax unit files if any of the following apply:
    1. They are legally required to file (IRC § 6012)
    2. They are eligible for refundable credits and would file to claim them
    3. They would file voluntarily for other reasons (state requirements,
       documentation, habit)

    The propensity variables (would_file_if_eligible_for_refundable_credit
    and would_file_taxes_voluntarily) are assigned during microdata
    construction.
    """
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/6012"

    def formula(tax_unit, period, parameters):
        # Required to file based on income thresholds
        required = tax_unit("tax_unit_is_required_to_file", period)

        # Would file to claim refundable credits (EITC, CTC, etc.)
        eligible_for_credits = tax_unit(
            "eligible_for_refundable_credits", period
        )
        would_file_for_credits = tax_unit(
            "would_file_if_eligible_for_refundable_credit", period
        )
        files_for_credits = eligible_for_credits & would_file_for_credits

        # Would file voluntarily for other reasons
        files_voluntarily = tax_unit("would_file_taxes_voluntarily", period)

        return required | files_for_credits | files_voluntarily
