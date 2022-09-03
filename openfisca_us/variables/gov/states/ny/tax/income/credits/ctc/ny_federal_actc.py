from openfisca_us.model_api import *


class ny_federal_actc(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY federal ACTC"
    unit = USD
    documentation = "The version of the federal ACTC used to determine the NY Empire State Child Credit."
    definition_period = YEAR
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        ctc = parameters(
            "2017-01-01"
        ).gov.irs.credits.ctc  # Federal ACTC, but with pre-TCJA parameters

        total_ctc = tax_unit("ctc", period)
        maximum_refundable_ctc = min_(
            add(tax_unit, period, ["ctc_refundable_individual_maximum"]),
            total_ctc,
        )

        # The other part of the "lesser of" statement is: "the amount by which [the non-refundable CTC]
        # would increase if [tax liability] increased by tax_increase", where tax_increase is the greater of:
        # - the phase-in amount
        # - Social Security tax minus the EITC
        # First, we find tax_increase:

        earnings = add(tax_unit, period, ["earned_income"])
        earnings_over_threshold = max_(
            0, earnings - ctc.refundable.phase_in.threshold
        )
        relevant_earnings = (
            earnings_over_threshold * ctc.refundable.phase_in.rate
        )

        # Compute "Social Security taxes" as defined in the US Code for the ACTC.
        # This includes OASDI and Medicare payroll taxes, as well as half
        # of self-employment taxes.
        PERSON_VARIABLES = [
            "employee_social_security_tax",
            "employee_medicare_tax",
            "unreported_payroll_tax",
        ]
        PERSON_VARIABLES_SUBTRACT = ["excess_payroll_tax_withheld"]
        TAX_UNIT_VARIABLES = [
            "c03260",  # Deductible portion of the self-employed tax.
            "additional_medicare_tax",
        ]
        social_security_tax = (
            add(tax_unit, period, PERSON_VARIABLES)
            + add(tax_unit, period, TAX_UNIT_VARIABLES)
            - add(tax_unit, period, PERSON_VARIABLES_SUBTRACT)
        )
        eitc = tax_unit("eitc", period)
        social_security_excess = max_(0, social_security_tax - eitc)
        qualifying_children = add(
            tax_unit, period, ["is_ctc_qualifying_child"]
        )
        tax_increase = where(
            qualifying_children
            < ctc.refundable.phase_in.min_children_for_ss_taxes_minus_eitc,
            relevant_earnings,
            max_(relevant_earnings, social_security_excess),
        )
        limiting_tax = tax_unit("ctc_limiting_tax_liability", period)
        ctc_capped_by_tax = min_(total_ctc, limiting_tax)
        ctc_capped_by_increased_tax = min_(
            total_ctc, limiting_tax + tax_increase
        )
        amount_ctc_would_increase = (
            ctc_capped_by_increased_tax - ctc_capped_by_tax
        )

        ny_federal_actc = min_(
            maximum_refundable_ctc, amount_ctc_would_increase
        )

        remaining_unused_ctc = tax_unit(
            "ny_federal_ctc_max", period
        ) - tax_unit("ny_federal_non_refundable_ctc", period)
        return min_(ny_federal_actc, remaining_unused_ctc)
