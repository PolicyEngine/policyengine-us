from policyengine_us.model_api import *


class ct_ssp_earned_income_disregard(Variable):
    value_type = float
    entity = Person
    label = "Connecticut SSP earned income disregard"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CT
    reference = (
        "https://www.ctdssmap.com/CTPortal/Information/Get/UPM#5030.10",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ct.html",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ct.dss.ssp.disregard.earned
        gross_earned = add(
            person,
            period,
            [
                "ssi_earned_income",
                "ssi_earned_income_deemed_from_ineligible_spouse",
            ],
        )
        is_blind = person("is_blind", period.this_year)

        initial = where(
            is_blind,
            p.blind_initial,
            p.aged_disabled_initial,
        )
        rate = p.rate

        initial_disregard = min_(gross_earned, initial)
        remainder = max_(gross_earned - initial, 0)
        return initial_disregard + remainder * rate
