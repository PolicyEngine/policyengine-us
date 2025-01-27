from policyengine_us.model_api import *


class tax_unit_is_filer(Variable):
    value_type = float
    entity = TaxUnit
    label = "files taxes"
    unit = USD
    documentation = (
        "Whether this tax unit has a non-zero income tax liability."
    )
    definition_period = YEAR

    """
    (a) General rule
    Returns with respect to income taxes under subtitle A shall be made by the following:
    (1)
    (A) Every individual having for the taxable year gross income which equals or exceeds the exemption amount, except that a return shall not be required of an individual—
    (i) who is not married (determined by applying section 7703), is not a surviving spouse (as defined in section 2(a)), is not a head of a household (as defined in section 2(b)), and for the taxable year has gross income of less than the sum of the exemption amount plus the basic standard deduction applicable to such an individual,
    (ii) who is a head of a household (as so defined) and for the taxable year has gross income of less than the sum of the exemption amount plus the basic standard deduction applicable to such an individual,
    (iii) who is a surviving spouse (as so defined) and for the taxable year has gross income of less than the sum of the exemption amount plus the basic standard deduction applicable to such an individual, or
    (iv) who is entitled to make a joint return and whose gross income, when combined with the gross income of his spouse, is, for the taxable year, less than the sum of twice the exemption amount plus the basic standard deduction applicable to a joint return, but only if such individual and his spouse, at the close of the taxable year, had the same household as their home.
    Clause (iv) shall not apply if for the taxable year such spouse makes a separate return or any other taxpayer is entitled to an exemption for such spouse under section 151(c).
    (B) The amount specified in clause (i), (ii), or (iii) of subparagraph (A) shall be increased by the amount of 1 additional standard deduction (within the meaning of section 63(c)(3)) in the case of an individual entitled to such deduction by reason of section 63(f)(1)(A) (relating to individuals age 65 or more), and the amount specified in clause (iv) of subparagraph (A) shall be increased by the amount of the additional standard deduction for each additional standard deduction to which the individual or his spouse is entitled by reason of section 63(f)(1).
    (C) The exception under subparagraph (A) shall not apply to any individual—
    (i) who is described in section 63(c)(5) and who has—
    (I) income (other than earned income) in excess of the sum of the amount in effect under section 63(c)(5)(A) plus the additional standard deduction (if any) to which the individual is entitled, or
    (II) total gross income in excess of the standard deduction, or
    (ii) for whom the standard deduction is zero under section 63(c)(6).
    (D) For purposes of this subsection—
    (i) The terms "standard deduction", "basic standard deduction" and "additional standard deduction" have the respective meanings given such terms by section 63(c).
    (ii) The term "exemption amount" has the meaning given such term by section 151(d). In the case of an individual described in section 151(d)(2), the exemption amount shall be zero.
    """

    def formula(tax_unit, period, parameters):
        gross_income = add(tax_unit, period, ["irs_gross_income"])
        exemption_amount = parameters(period).gov.irs.income.exemption.amount

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

        # (a)(1)(C)

        unearned_income_threshold = 500 + tax_unit(
            "additional_standard_deduction", period
        )
        unearned_income = gross_income - add(
            tax_unit, period, ["earned_income"]
        )
        unearned_income_over_threshold = (
            unearned_income > unearned_income_threshold
        )

        required_to_file = (
            income_over_exemption_amount | unearned_income_over_threshold
        )

        tax_refund = tax_unit("income_tax", period) < 0
        not_required_but_likely_filer = ~required_to_file & tax_refund

        # (a)(1)(D) is just definitions

        return required_to_file | not_required_but_likely_filer
