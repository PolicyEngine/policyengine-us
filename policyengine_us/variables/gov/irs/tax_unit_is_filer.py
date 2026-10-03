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
    3. They claim a section 911 exclusion and would file to claim a tax
       benefit (the exclusion is claimed on Form 2555 with a return)
    4. They would file voluntarily for other reasons (state requirements,
       documentation, habit)

    The propensity variables (would_file_if_eligible_for_refundable_credit
    and would_file_taxes_voluntarily) are assigned during microdata
    construction.
    """
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/6012",
        # A section 911 election is filed with the return for its first year
        # and then stays in effect.
        "https://www.law.cornell.edu/cfr/text/26/1.911-7",
        # "in the case of an individual claiming an exclusion under section
        # 911, he shall attach Form 2555 to the return required under this
        # paragraph"
        "https://www.law.cornell.edu/cfr/text/26/1.6012-1",
        # "Attach Form 2555 to Form 1040 or 1040-SR when filed."
        "https://www.irs.gov/pub/irs-pdf/i2555.pdf#page=2",
    )

    def formula(tax_unit, period, parameters):
        # Required to file based on income thresholds
        required = tax_unit("tax_unit_is_required_to_file", period)

        # Would file to claim refundable credits (EITC, CTC, etc.)
        eligible_for_credits = tax_unit("eligible_for_refundable_credits", period)
        would_file_for_credits = tax_unit(
            "would_file_if_eligible_for_refundable_credit", period
        )
        files_for_credits = eligible_for_credits & would_file_for_credits

        # Would file voluntarily for other reasons
        files_voluntarily = tax_unit("would_file_taxes_voluntarily", period)

        # A section 911 exclusion is claimed on Form 2555 attached to a
        # return (Treas. Reg. 1.911-7(a)(1) and 1.6012-1(a)(3)). Sections
        # 24(d)(3) and 32(c)(1)(C) deny the claimant the refundable credits,
        # so those credits cannot be its reason to file. A claimant under the
        # filing threshold need not file in a later year of a continuing
        # election, so the propensity to file for a tax benefit decides.
        claims_section_911 = tax_unit("foreign_earned_income_exclusion", period) > 0
        files_for_section_911 = claims_section_911 & would_file_for_credits

        return required | files_for_credits | files_for_section_911 | files_voluntarily
