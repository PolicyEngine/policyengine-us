from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ca.cdss.state_supplement._ca_state_supplement_rates import (
    ca_in_title_xix_facility,
    ca_state_supplement_rates,
)


def ca_capi_couple_computation(person, period):
    """Whether CAPI and SSP compute the person with their spouse as a couple.

    SSI's couple computation, except that a couple with exactly one spouse in
    a Title XIX facility is computed separately (20 CFR 416.414(b)(3)), when
    only the California facility input marks it. Only a head or spouse is in a
    couple, because a situation with no marital units puts a dependent in the
    couple's unit.
    """
    head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
    in_facility = ca_in_title_xix_facility(person, period)
    one_in_facility = person.marital_unit.sum(in_facility & head_or_spouse) == 1
    return (
        person("ssi_couple_computation_applies", period)
        & ~one_in_facility
        & head_or_spouse
    )


def ca_capi_spouse_ssi_ssp(person, period):
    """Return the SSI and state supplement paid to the person's spouse.

    Only a head or spouse who is not CAPI-eligible counts.
    """
    head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
    spouse = ~person("ca_capi_eligible_person", period.this_year) & head_or_spouse
    payment = add(person, period, ["ssi", "ca_state_supplement_person"])
    return person.marital_unit.sum(payment * spouse)


def ca_capi_ssi_ssp_standard(person, period, parameters):
    """Return a person's monthly SSI/SSP individual and couple standards.

    CAPI equals SSI/SSP (WIC 18941), so each standard is the federal amount for
    the living arrangement plus California's share. Each spouse in a joint
    computation supplies half of the couple total, half the couple amount per
    person in non-medical out-of-home care (MPP 49-050.24).
    """
    fbr = parameters(period).gov.ssa.ssi.amount
    joint = ca_capi_couple_computation(person, period)
    individual_rate, couple_rate = ca_state_supplement_rates(
        person, period, parameters, joint
    )
    medical_facility = ca_in_title_xix_facility(person, period)
    # NOTE: the state shares before 2013 are the 1991 totals in WIC 12200 less
    # the 1991 federal rates (issue 10480).
    individual = individual_rate + where(
        medical_facility, fbr.medical_facility, fbr.individual
    )
    couple_federal = where(medical_facility, 2 * fbr.medical_facility, fbr.couple)
    couple = couple_federal + where(
        joint, person.marital_unit.sum(couple_rate / 2), couple_rate
    )
    return individual, couple
