from policyengine_us.model_api import *


class ma_rent_deduction_available(Variable):
    """Support the documented calculation, not general legal eligibility.

    Qualifying receipts must match actual return roles. Missing or contradictory
    claimant coverage leaves the compatibility estimate uncertified. A paired
    alternative election is unsupported; no spouse link is inferred here.
    """

    value_type = bool
    entity = TaxUnit
    label = "Massachusetts rent deduction is supported by qualified facts"
    definition_period = YEAR
    default_value = False
    defined_for = StateCode.MA
    reference = (
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section3",
        "https://www.mass.gov/info-details/deductions-on-rent-paid-in-massachusetts",
        "https://www.mass.gov/doc/2025-form-1-instructions/download",
    )

    def formula_2025_01_01(tax_unit, period, parameters):
        p = parameters(period).gov.states.ma.tax.income.deductions.rent
        filing_status = tax_unit("ma_filing_status", period)
        statuses = filing_status.possible_values
        is_joint = filing_status == statuses.JOINT
        is_separate = filing_status == statuses.SEPARATE
        person = tax_unit.members
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        dependent = person("is_tax_unit_dependent", period)
        joint_member = person.tax_unit("ma_filing_status", period) == statuses.JOINT
        claimant = head | (spouse & joint_member)
        roles_available = (tax_unit.sum(head) == 1) & (
            ~is_joint
            | ((tax_unit.sum(spouse) == 1) & (tax_unit.sum(head & spouse) == 0))
        )
        roles_available &= tax_unit.sum(claimant & dependent) == 0
        rent = person("ma_rent_deduction_qualifying_rent_paid", period)
        rent_known = person("ma_rent_deduction_qualifying_rent_paid_known", period)
        rent_valid = rent_known & np.isfinite(rent) & (rent >= 0)
        qualified_rent = tax_unit.sum(where(claimant & rent_valid, rent, 0))
        expenses_available = (
            roles_available
            & (tax_unit.sum(claimant & ~rent_valid) == 0)
            & np.isfinite(qualified_rent)
        )

        election = tax_unit("ma_rent_deduction_allocation_election", period)
        elections = election.possible_values
        spouse_status = tax_unit("ma_rent_deduction_spouse_facts_status", period)
        spouse_amount = tax_unit("ma_rent_deduction_spouse_amount_taken", period)
        spouse_amount_known = tax_unit(
            "ma_rent_deduction_spouse_amount_taken_known", period
        )
        couple_cap = p.cap[statuses.JOINT]
        spouse_amount_valid = (
            spouse_amount_known
            & np.isfinite(spouse_amount)
            & (spouse_amount >= 0)
            & (spouse_amount <= couple_cap)
        )
        external_return_available = (
            spouse_status == spouse_status.possible_values.VERIFIED_EXTERNAL_RETURN
        ) & spouse_amount_valid
        safe_spouse_amount = where(spouse_amount_valid, spouse_amount, 0)
        own_maximum = min_(p.share * qualified_rent, couple_cap - safe_spouse_amount)
        documentation = tax_unit("ma_rent_deduction_allocation_documentation", period)
        documentation_available = (own_maximum <= p.cap[statuses.SEPARATE]) | (
            documentation == documentation.possible_values.VERIFIED
        )
        alternative_available = (
            (election == elections.ALTERNATIVE)
            & external_return_available
            & documentation_available
        )
        return expenses_available & (
            ~is_separate
            | (election == elections.NO_ALTERNATIVE)
            | alternative_available
        )
