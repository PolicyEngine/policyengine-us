from policyengine_us.model_api import *


class rrc_caa(Variable):
    value_type = float
    entity = TaxUnit
    label = "Recovery Rebate Credit (CAA)"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/6428A",
        "https://www.law.cornell.edu/uscode/text/26/6428A#g",
    )

    def formula(tax_unit, period, parameters):
        rrc = parameters(period).gov.irs.credits.recovery_rebate_credit
        filing_status = tax_unit("filing_status", period)
        agi = tax_unit("adjusted_gross_income", period)
        # Count adults with valid SSN per 26 USC 6428A(g)(1) and (g)(2)
        adults_with_ssn = tax_unit("rrc_adult_count_with_valid_ssn", period)
        # Armed Forces exception per 26 USC 6428A(g)(5)
        armed_forces_exception = tax_unit(
            "rrc_qualifies_for_armed_forces_exception", period
        )
        is_joint = tax_unit("tax_unit_is_joint", period)
        count_adults = where(
            armed_forces_exception,
            2,  # Joint filers always have 2 adults (structural constant)
            where(is_joint, adults_with_ssn, min_(adults_with_ssn, 1)),
        )
        # Per 26 USC 6428A(g)(3), children count only if:
        # (i) at least one filer has valid SSN, AND
        # (ii) the child has valid SSN
        children_with_ssn = tax_unit(
            "rrc_cares_qualifying_children_with_valid_ssn", period
        )
        count_children = where(adults_with_ssn > 0, children_with_ssn, 0)
        max_payment = (
            rrc.caa.max.adult * count_adults
            + rrc.caa.max.child * count_children
        )
        payment_reduction = rrc.caa.phase_out.rate * max_(
            0, agi - rrc.caa.phase_out.threshold[filing_status]
        )
        return max_(0, max_payment - payment_reduction)
