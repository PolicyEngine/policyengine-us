from policyengine_us.model_api import *


class rrc_arpa(Variable):
    value_type = float
    entity = TaxUnit
    label = "Recovery Rebate Credit (ARPA)"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/6428B",
        "https://www.law.cornell.edu/uscode/text/26/6428B#e_2",
    )

    def formula(tax_unit, period, parameters):
        rrc = parameters(period).gov.irs.credits.recovery_rebate_credit
        filing_status = tax_unit("filing_status", period)
        agi = tax_unit("adjusted_gross_income", period)
        # Count dependents with valid SSN per 26 USC 6428B(e)(2)(C)
        # ARPA expanded to all dependents (not just qualifying children)
        count_dependents = tax_unit(
            "rrc_arpa_dependents_with_valid_ssn", period
        )
        # Count adults with valid SSN per 26 USC 6428B(e)(2)(A)-(B)
        # Armed Forces exception per 26 USC 6428B(e)(2)(E)
        armed_forces_exception = tax_unit(
            "rrc_qualifies_for_armed_forces_exception", period
        )
        is_joint = tax_unit("tax_unit_is_joint", period)
        adults_with_ssn = tax_unit("rrc_adult_count_with_valid_ssn", period)
        count_adults = where(
            armed_forces_exception,
            2,  # Joint filers always have 2 adults (structural constant)
            where(is_joint, adults_with_ssn, min_(adults_with_ssn, 1)),
        )
        max_payment = (
            rrc.arpa.max.adult * count_adults
            + rrc.arpa.max.dependent * count_dependents
        )
        phase_out_length = rrc.arpa.phase_out.length[filing_status]
        excess = max_(0, agi - rrc.arpa.phase_out.threshold[filing_status])
        payment_reduction_percent = excess / phase_out_length
        payment_reduction = max_payment * payment_reduction_percent
        return max_(0, max_payment - payment_reduction)
