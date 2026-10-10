from policyengine_us.model_api import *


class va_claims_eitc_disqualifying_benefits(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Filer claims the Virginia benefits that bar the EITC and low-income credit"
    documentation = "Whether the filer claims the National Guard, military basic pay and federal or state employee subtractions, the aged or blind exemptions and the age deduction, rather than forgoing them to claim the Virginia low-income credit or EITC."
    definition_period = YEAR
    defined_for = StateCode.VA
    default_value = True
    reference = (
        "https://law.lis.virginia.gov/vacode/title58.1/chapter3/section58.1-339.8/",
        # Form 760 lines 4 and 12: "Claim the deduction or subtraction that
        # gives you the greatest tax benefit."
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2025-760-instructions.pdf#page=15",
    )

    def formula(tax_unit, period, parameters):
        # Va. Code 58.1-339.8(D) bars the credits in a year in which the
        # filers "claim" a listed benefit, so a filer entitled to one chooses
        # between the benefits and a credit. Tax net of refundable credits is
        # lowest under the better choice. A tie keeps the benefits; it also
        # covers returns with no listed benefit, which lose no credit by
        # "claiming" none.
        tax_if_claiming_benefits = tax_unit(
            "va_income_tax_if_claiming_eitc_disqualifying_benefits", period
        )
        tax_if_claiming_refundable_eitc = tax_unit(
            "va_income_tax_if_claiming_refundable_eitc", period
        )
        tax_if_claiming_non_refundable_eitc = tax_unit(
            "va_income_tax_if_claiming_non_refundable_eitc", period
        )
        return tax_if_claiming_benefits <= min_(
            tax_if_claiming_refundable_eitc, tax_if_claiming_non_refundable_eitc
        )
