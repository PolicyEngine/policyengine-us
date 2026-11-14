from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_total,
    _ssi_spouse_index,
)
from policyengine_us.variables.gov.states.ca.cdss.state_supplement._ca_state_supplement_rates import (
    ca_in_title_xix_facility,
    ca_state_supplement_rates,
)


def ca_capi_couple_computation(person, period):
    """Whether CAPI and SSP compute the person with their spouse as a couple.

    SSI's couple computation, except that a couple with exactly one spouse in
    a Title XIX facility is computed separately (20 CFR 416.414(b)(3)), when
    only the California facility input marks it. The facility count covers
    the person and the spouse SSI's spouse test identifies, so the default
    marital unit of a situation that omits marital units adds no one else.
    """
    in_facility = ca_in_title_xix_facility(person, period)
    one_in_facility = (
        _ssi_couple_total(person, period.this_year, in_facility.astype(int)) == 1
    )
    return person("ssi_couple_computation_applies", period) & ~one_in_facility


def ca_capi_spouse_ssi_ssp(person, period):
    """Return the SSI and state supplement paid to the person's spouse.

    Only a spouse, as SSI's spouse test identifies one, who is not
    CAPI-eligible counts.
    """
    spouse_index = _ssi_spouse_index(person, period.this_year)
    safe_spouse = np.maximum(spouse_index, 0)
    spouse = (spouse_index >= 0) & ~person("ca_capi_eligible_person", period.this_year)[
        safe_spouse
    ]
    payment = add(person, period, ["ssi", "ca_state_supplement_person"])
    return payment[safe_spouse] * spouse


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
        joint, _ssi_couple_total(person, period.this_year, couple_rate / 2), couple_rate
    )
    return individual, couple
