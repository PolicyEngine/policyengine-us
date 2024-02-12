from policyengine_us.model_api import *


class or_federal_tax_liability_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR federal tax liability subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-17_101-431_2021.pdf#page=71",
        "https://www.oregonlegislature.gov/bills_laws/ors/ors316.html",  # Subsection 316.800
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        # Federal tax liability
        federal_itax = tax_unit("income_tax", period)
        # child and dependent tax credit, excluding 2022 and on
        non_refundable_ctc = tax_unit("non_refundable_ctc", period)
        refundable_ctc = tax_unit("refundable_ctc", period)
        cdcc = tax_unit("cdcc", period)

        year = period.start.year
        if year >= 2022:
            non_refundable_ctc = refundable_ctc = cdcc = 0

        # American opportunity credit
        american_opportunity_credit = tax_unit(
            "american_opportunity_credit", period
        )
        # recovery rebate credit
        recovery_rebate_credit = tax_unit("recovery_rebate_credit", period)
        # Premium tax credit
        premium_tax_credit = tax_unit("premium_tax_credit", period)

        federal_itax_inclusive = federal_itax + non_refundable_ctc
        other_taxes_exclusive = (
            refundable_ctc
            + american_opportunity_credit
            + recovery_rebate_credit
            + premium_tax_credit
            + cdcc
        )
        # Other taxes and any additions to tax - not modelled here
        # Federal economic stimulus payments - not modelled here
        # Excess advance premium tax credit - not modelled here
        or_federal_income_tax = max_(
            0, federal_itax_inclusive - other_taxes_exclusive
        )

        # limit subtraction based on caps scaled to federal AGI
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        caps = (
            parameters(period)
            .gov.states["or"]
            .tax.income.subtractions.federal_tax_liability.cap
        )
        federal_agi = tax_unit("adjusted_gross_income", period)
        cap = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.SEPARATE,
                filing_status == status.WIDOW,
            ],
            [
                caps.single.calc(federal_agi),
                caps.joint.calc(federal_agi),
                caps.head_of_household.calc(federal_agi),
                caps.separate.calc(federal_agi),
                caps.widow.calc(federal_agi),
            ],
        )
        return min_(or_federal_income_tax, cap)
