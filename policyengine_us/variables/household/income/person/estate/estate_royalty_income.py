from policyengine_us.model_api import *


class estate_royalty_income(Variable):
    value_type = float
    entity = Person
    label = "Estate and trust royalties"
    unit = USD
    documentation = (
        "Royalties included in estate_income that are not derived in the "
        "ordinary course of a trade or business, net of the deductions and "
        "interest clearly and directly allocable to them: Schedule K-1 (Form "
        "1041) box 5 royalties, reported in Schedule E Part III column (f). "
        "Sections 652(b) and 662(b) give a beneficiary's share of trust income "
        "the character it had in the trust, so 26 USC 32(i)(2)(C) counts these "
        "royalties as disqualified income for the EITC. Publication 596 "
        "Worksheet 1 line 8 takes royalties only from Schedule E line 23b "
        "(Part I) and so leaves them out; the model follows the statute. "
        "Enter income as a positive amount and a net loss as a negative "
        "amount. The default is zero. This classifies income already counted "
        "in estate_income and does not represent additional income; box 5 "
        "also holds annuities and income in respect of a decedent, which are "
        "not royalties and are not included here. The input is not checked "
        "against estate_income or passive_estate_income."
    )
    definition_period = YEAR
    default_value = 0
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/32#i_2_C",
        "https://www.law.cornell.edu/uscode/text/26/652#b",
        "https://www.law.cornell.edu/uscode/text/26/662#b",
        "https://www.irs.gov/pub/irs-prior/p596--2025.pdf#page=7",
        "https://www.irs.gov/pub/irs-prior/f1041sk1--2025.pdf#page=2",
        "https://www.irs.gov/pub/irs-prior/i1041sk1--2025.pdf#page=2",
    )
