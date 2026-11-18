from policyengine_us.model_api import *


class rrc_cares(Variable):
    value_type = float
    entity = TaxUnit
    label = "Recovery Rebate Credit (CARES)"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/6428",
        "https://www.law.cornell.edu/uscode/text/26/6428#g",
    )

    def formula(tax_unit, period, parameters):
        rrc = parameters(period).gov.irs.credits.recovery_rebate_credit
        filing_status = tax_unit("filing_status", period)
        agi = tax_unit("adjusted_gross_income", period)
        # Count adults with valid SSN per 26 USC 6428(g)(1)(A) and (g)(1)(B)
        adults_with_ssn = tax_unit("rrc_adult_count_with_valid_ssn", period)
        # Armed Forces exception per 26 USC 6428(g)(4)
        armed_forces_exception = tax_unit(
            "rrc_qualifies_for_armed_forces_exception", period
        )
        is_joint = tax_unit("tax_unit_is_joint", period)
        # The exception waives the identification rule, not the exclusion of
        # a spouse who is another taxpayer's dependent.
        person = tax_unit.members
        dependent_filers = tax_unit.sum(
            person("is_tax_unit_head_or_spouse", period)
            & person("claimable_as_dependent_on_another_return", period)
        )
        count_adults = where(
            armed_forces_exception,
            # Joint filers always have 2 adults (structural constant)
            max_(2 - dependent_filers, 0),
            where(is_joint, adults_with_ssn, min_(adults_with_ssn, 1)),
        )
        # Per 26 USC 6428(g)(1)(C), children count only if:
        # (i) at least one filer has valid SSN, AND
        # (ii) the child has valid SSN
        children_with_ssn = tax_unit(
            "rrc_cares_qualifying_children_with_valid_ssn", period
        )
        # This prerequisite is a spouse with a valid SSN, whether or not that
        # spouse is an eligible individual; the credit itself needs a filer
        # who is not a dependent of another taxpayer.
        filer_has_ssn = tax_unit.any(
            person("is_tax_unit_head_or_spouse", period)
            & person("meets_eitc_identification_requirements", period)
        )
        no_eligible_filer = tax_unit("every_filer_is_dependent_elsewhere", period)
        count_children = where(filer_has_ssn & ~no_eligible_filer, children_with_ssn, 0)
        max_payment = (
            rrc.cares.max.adult * count_adults + rrc.cares.max.child * count_children
        )
        payment_reduction = rrc.cares.phase_out.rate * max_(
            0, agi - rrc.cares.phase_out.threshold[filing_status]
        )
        return max_(0, max_payment - payment_reduction)
