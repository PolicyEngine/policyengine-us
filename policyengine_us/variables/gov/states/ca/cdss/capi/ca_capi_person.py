from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ca.cdss.capi._ca_capi_ssi_ssp_standard import (
    ca_capi_ssi_ssp_standard,
)


class ca_capi_person(Variable):
    value_type = float
    entity = Person
    label = "California CAPI amount per person"
    unit = USD
    definition_period = MONTH
    defined_for = "ca_capi_eligible_person"
    reference = (
        # PDF pages 25, 30, 47
        "https://www.cdss.ca.gov/Portals/9/CAPI/CAPI_Regulations-Accessible.pdf#page=25",
        "https://secure.ssa.gov/poms.nsf/lnx/0501320430",
    )

    def formula(person, period, parameters):
        countable_income = person("ssi_countable_income", period)
        payment_standard = person("ca_capi_payment_standard", period)
        benefit = max_(payment_standard - countable_income, 0)

        # MPP 49-035.71 follows the SSI spouse-to-spouse deeming steps: compute
        # the federal and state parts as an individual and under deeming, then
        # take the lesser of each (POMS SI 01320.430 D).
        # NOTE: the federal parts use the independent-living benefit rates,
        # matching the independent-living SSI/SSP standards.
        individual_standard, couple_standard = ca_capi_ssi_ssp_standard(
            person, period, parameters
        )
        fbr = parameters(period).gov.ssa.ssi.amount
        deemed_income = person("ssi_income_deemed_from_ineligible_spouse", period)
        own_income = max_(countable_income - deemed_income, 0)
        individual_federal = fbr.individual - own_income
        couple_federal = fbr.couple - countable_income
        federal = max_(min_(individual_federal, couple_federal), 0)
        individual_supplement = individual_standard - fbr.individual
        couple_supplement = max_(couple_standard - fbr.couple, individual_supplement)
        # Income above a federal rate reduces the matching state supplement.
        supplement = min_(
            individual_supplement + min_(individual_federal, 0),
            couple_supplement + min_(couple_federal, 0),
        )
        p = parameters(period).gov.states.ca.cdss.capi.payment_standard_offset
        deemed_benefit = max_(federal + supplement - p.single, 0)
        deeming = person("is_ssi_spousal_deeming_applies", period.this_year) & ~person(
            "ssi_couple_computation_applies", period
        )
        return where(deeming, deemed_benefit, benefit)
