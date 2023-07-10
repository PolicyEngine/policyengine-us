from policyengine_us.model_api import *


class mi_standard_deduction_increase(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan standard deduction increase"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Michigan standard deduction increase of qualifying age and condition."
    )
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=15",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.deductions.standard.increase
        # Core deduction based on filing status.
        filing_status = tax_unit("filing_status", period)

        age_older = tax_unit("greater_age_head_spouse", period)
        # Michigan standard deduction increase
        sdi_birth_year = -(age_older - period.start.year)
        sdi_age_eligibility = (sdi_birth_year >= p.min_birth_year) & (
            sdi_birth_year <= p.max_birth_year
        )
        sdi_amount = p.amount[filing_status]

        return (
            sdi_age_eligibility
            * sdi_amount
            * (
                tax_unit("social_security_exempt_retirement_benefits", period)
                > 0
            )
        )
