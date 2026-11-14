from policyengine_us.model_api import *


class ma_rent_deduction(Variable):
    """Maximum supported rent component, with an uncertified legacy fallback.

    The documented alternative holds the external spouse's actual claim fixed.
    It does not reconstruct a joint agreement or solve simultaneous returns.
    Read ma_rent_deduction_available before treating this output as verified.
    """

    value_type = float
    entity = TaxUnit
    label = "Massachusetts rent deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = (
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section3",
        "https://www.mass.gov/info-details/deductions-on-rent-paid-in-massachusetts",
        "https://www.mass.gov/doc/2025-form-1-instructions/download",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ma.tax.income.deductions.rent
        filing_status = tax_unit("ma_filing_status", period)
        rent = add(tax_unit, period, ["rent"])
        return min_(p.share * rent, p.cap[filing_status])

    def formula_2025_01_01(tax_unit, period, parameters):
        p = parameters(period).gov.states.ma.tax.income.deductions.rent
        filing_status = tax_unit("ma_filing_status", period)
        statuses = filing_status.possible_values
        legacy_rent = add(tax_unit, period, ["rent"])
        legacy_deduction = min_(p.share * legacy_rent, p.cap[filing_status])
        person = tax_unit.members
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        joint_member = person.tax_unit("ma_filing_status", period) == statuses.JOINT
        claimant = head | (spouse & joint_member)
        rent = person("ma_rent_deduction_qualifying_rent_paid", period)
        rent_valid = np.isfinite(rent) & (rent >= 0)
        qualified_rent = tax_unit.sum(where(claimant & rent_valid, rent, 0))

        election = tax_unit("ma_rent_deduction_allocation_election", period)
        alternative = (filing_status == statuses.SEPARATE) & (
            election == election.possible_values.ALTERNATIVE
        )
        spouse_amount = tax_unit("ma_rent_deduction_spouse_amount_taken", period)
        couple_cap = p.cap[statuses.JOINT]
        spouse_amount_valid = (
            np.isfinite(spouse_amount)
            & (spouse_amount >= 0)
            & (spouse_amount <= couple_cap)
        )
        safe_spouse_amount = where(spouse_amount_valid, spouse_amount, 0)
        cap = where(alternative, couple_cap - safe_spouse_amount, p.cap[filing_status])
        supported_deduction = min_(p.share * qualified_rent, cap)
        available = tax_unit("ma_rent_deduction_available", period)
        return where(available, supported_deduction, legacy_deduction)
