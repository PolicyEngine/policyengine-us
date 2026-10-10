from policyengine_us.model_api import *


# Person-level sources whose losses make up the business part of loss_ald.
BUSINESS_LOSS_SOURCES = [
    "total_self_employment_income",
    "farm_operations_income",
    "rental_income",
    "farm_rent_income",
    "estate_income",
    "partnership_s_corp_income",
]
CAPITAL_GAIN_CHARACTERS = ["short_term_capital_gains", "long_term_capital_gains"]


class mo_federal_adjusted_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Missouri federal adjusted gross income"
    documentation = (
        "Each filer's federal adjusted gross income on Form MO-1040, Line 1. "
        "On a combined return each spouse's column holds their own income, "
        "losses and federal adjustments to income, and the two columns add up "
        "to the joint federal adjusted gross income. From 2024 a negative "
        "amount is replaced by zero."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        # PDF pages 6-7: Line 1 and its worksheet. "The combined income for
        # you and your spouse must equal the total federal adjusted gross
        # income you reported on your federal return."
        "https://dor.mo.gov/forms/MO-1040%20Instructions_2023.pdf#page=6",
        # Line 1: "enter $0" for a negative federal adjusted gross income.
        "https://dor.mo.gov/forms/MO-1040%20Instructions_2024.pdf#page=6",
        # Negative Federal Adjusted Gross Income, citing 12 CSR 10-2.710.
        "https://dor.mo.gov/forms/MO-1040%20Instructions_2025.pdf#page=6",
        # PDF pages 1-4: 12 CSR 10-2.010(2), capital losses go to "the
        # spouse responsible", and (4), each spouse's federal AGI as if on a
        # separate federal return (effective February 29, 2024).
        "https://dor.mo.gov/resources/official-final-rules/documents/12_CSR_10-2_010.pdf#page=1",
        # 12 CSR 10-2.010(5), effective April 30, 2026.
        "https://dor.mo.gov/resources/official-final-rules/documents/12_CSR_10-2_010_Income_Tax_of_Current_or_Former_Spouses.pdf#page=4",
        "https://www.law.cornell.edu/regulations/missouri/12-CSR-10-2-710",
        "https://revisor.mo.gov/main/OneSection.aspx?section=143.121",
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        # The head and spouse are the filers; a tax unit dependent's income
        # and deductions are on their own return, as in irs_gross_income.
        filer = ~person("is_tax_unit_dependent", period)
        # Items that belong to the couple rather than to one spouse are
        # divided equally between them.
        equal_share = filer / max_(tax_unit.sum(filer), 1)

        def attribute(own, amount):
            # Divide a tax-unit amount in proportion to the filers' own
            # amounts, or equally when they have none. Use a mask rather than
            # where to avoid a divide-by-zero warning.
            own = filer * own
            total = tax_unit.sum(own)
            share = np.array(equal_share, dtype=float)
            mask = total > 0
            share[mask] = own[mask] / total[mask]
            return amount * share

        # Federal adjustments to income (Line 1 worksheet, "Subtract: federal
        # adjustments to income"), each in the column of the spouse it belongs
        # to. 12 CSR 10-2.010(4), effective February 29, 2024, puts each
        # spouse's column on a separate-return basis.
        p = parameters(period).gov.irs.ald
        adjustments = 0
        for deduction in p.deductions:
            if deduction == "loss_ald":
                continue
            if person.entity.get_variable(
                deduction, check_existence=True
            ).entity.is_person:
                own = person(deduction, period)
                adjustments = adjustments + filer * own
                if deduction in p.filer_amounts_recorded_on_dependents:
                    # The filers' amounts recorded on a dependent.
                    adjustments = adjustments + equal_share * tax_unit.sum(~filer * own)
            elif person.entity.get_variable(f"{deduction}_person") is not None:
                adjustments = adjustments + attribute(
                    person(f"{deduction}_person", period), tax_unit(deduction, period)
                )
            else:
                adjustments = adjustments + equal_share * tax_unit(deduction, period)

        # Business and capital losses (loss_ald). The worksheet reports each
        # spouse's own business, rental, farm and capital gains or losses.
        loss_ald = tax_unit("loss_ald", period)
        allowed_against_gains = tax_unit("capital_losses_allowed_against_gains", period)
        limited_capital_loss = tax_unit("limited_capital_loss", period)
        business_loss = max_(0, loss_ald - allowed_against_gains - limited_capital_loss)
        # A Form 4797 loss is recorded for the tax unit, and its gain is
        # divided equally in other_net_gain_gross_income.
        own_business_loss = equal_share * max_(0, -tax_unit("other_net_gain", period))
        for source in BUSINESS_LOSS_SOURCES:
            own_business_loss = own_business_loss + max_(0, -person(source, period))
        own_capital_gain = max_(0, person("capital_gains", period)) + max_(
            0, person("non_sch_d_capital_gains", period)
        )
        own_capital_loss = person("capital_losses", period)
        # 12 CSR 10-2.010(2): when the couple's capital losses exceed their
        # gains, the excess deduction goes to "the spouse responsible for the
        # excess", pro rata when both are. In Examples 1-3 the gains drop out
        # of both columns, so the losses netted against them go to the
        # spouse with the gains. Responsibility follows the short-term and
        # long-term netting of Example 2. Otherwise each spouse's losses
        # netted against gains are their own.
        net_capital_loss = filer * own_capital_loss
        net_capital_gain = filer * own_capital_gain
        losses_exceed_gains = tax_unit.sum(net_capital_loss) > tax_unit.sum(
            net_capital_gain
        )
        allowed_share = where(
            losses_exceed_gains,
            attribute(own_capital_gain, allowed_against_gains),
            attribute(own_capital_loss, allowed_against_gains),
        )
        responsibility = 0
        for character in CAPITAL_GAIN_CHARACTERS:
            amount = filer * person(character, period)
            if character == "long_term_capital_gains":
                # Capital gain distributions are long-term gains.
                amount = amount + filer * max_(
                    0, person("non_sch_d_capital_gains", period)
                )
            excess = max_(0, -tax_unit.sum(amount))
            own_loss = max_(0, -amount)
            unit_loss = tax_unit.sum(own_loss)
            share = np.zeros_like(unit_loss)
            mask = unit_loss > 0
            share[mask] = own_loss[mask] / unit_loss[mask]
            responsibility = responsibility + excess * share
        # Without a short-term and long-term split, each spouse's net loss.
        responsibility = where(
            tax_unit.sum(responsibility) > 0, responsibility, own_capital_loss
        )
        limited_share = attribute(responsibility, limited_capital_loss)
        own_losses = (
            attribute(own_business_loss, business_loss) + allowed_share + limited_share
        )
        # Scale to loss_ald, in case it is set directly.
        parts = business_loss + allowed_against_gains + limited_capital_loss
        loss_share = np.array(equal_share * loss_ald, dtype=float)
        mask = parts > 0
        loss_share[mask] = own_losses[mask] * loss_ald[mask] / parts[mask]

        gross_income = person("irs_gross_income", period)
        separate_agi = filer * gross_income - loss_share - adjustments
        if parameters(period).gov.contrib.ubi_center.basic_income.taxable:
            separate_agi = separate_agi + equal_share * tax_unit("basic_income", period)

        p = parameters(period).gov.states.mo.tax.income.federal_agi
        if not p.negative_floor_applies:
            return separate_agi
        # 2025 MO-1040 instructions, page 6, and 12 CSR 10-2.010(5): when
        # joint federal AGI is zero or less, both spouses enter $0. When it is
        # positive, a spouse whose separate amount is negative enters $0 and
        # the other spouse enters the whole joint amount.
        joint_agi = tax_unit.sum(separate_agi)
        has_negative = tax_unit.any(separate_agi < 0)
        line_1 = where(
            separate_agi < 0,
            0,
            where(has_negative, joint_agi, separate_agi),
        )
        return filer * where(joint_agi > 0, line_1, 0)
