from policyengine_us.model_api import *


class ca_sf_caap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "San Francisco County CAAP"
    definition_period = MONTH
    defined_for = "ca_sf_caap_eligible"
    reference = (
        # SF Administrative Code Chapter 20, Article VII (County Adult
        # Assistance Programs), SEC. 20.7-21 / 20.7-24.
        "https://codelibrary.amlegal.com/codes/san_francisco/latest/sf_admin/0-0-0-65352",
        # CAAP Eligibility Manual (effective 2026-05-14).
        "https://www.sfhsa.org/sites/default/files/media/document/2026-05/manual_caap_eligibility_5_14_2026.pdf",
    )
    # This models the General Assistance (GA) tier only. We don't track the
    # following at the moment:
    #   - PAES / CALM / SSIP sub-program tiers and their activity gates
    #     (job-readiness, Medi-Cal linkage, disability + pending SSI).
    #   - The 15/30-day continuous-residency requirement (SEC. 20.7-11).
    #   - The real-property / home-value test (SEC. 20.7-12).
    #   - Asset exemptions beyond liquid cash (burial funds, life insurance,
    #     one vehicle); spm_unit_cash_assets already excludes these (SEC. 20.7-13).
    #   - Identification, finger/photo imaging, fleeing-felon, CalWORKs
    #     time-limit, and SUD-treatment gates (SEC. 20.7-16..20).
    #   - The Mandatory Direct Rent Payment routing (SEC. 20.7-33); we treat the
    #     full grant as received by the household.
    #   - The episodic housing supplement and +$50 cash payments (Div 94-14.1).

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.sf.caap
        max_grant = spm_unit("ca_sf_caap_max_grant", period)
        countable_income = spm_unit("ca_sf_caap_countable_income", period)
        # Fill-the-gap on cash income. Income is floored at zero because
        # self-employment income can be negative, which would otherwise inflate
        # the grant above the maximum (SEC. 20.7-21).
        grant_after_income = max_(max_grant - max_(countable_income, 0), 0)
        # In-kind value of housing/utilities/meals is deducted from the grant
        # (SEC. 20.7-22(c)), not the income test.
        in_kind = spm_unit("ca_sf_caap_income_in_kind", period)
        cash_grant = max_(grant_after_income - in_kind, 0)
        # Special allowance (SEC. 20.7-24): "A special allowance of up to $59 per
        # month shall be made available to any Recipient when the income-in-kind
        # value ... exceeds the maximum monthly grant ... If such income-in-kind
        # value does not exceed the maximum monthly grant ... but allows for less
        # than $59 cash per month, that Recipient shall receive an amount that,
        # when added to [the grant], equals $59 cash per month." Both branches
        # reduce to: when in-kind is present and leaves less than $59 cash, top
        # the recipient up to $59. We cap the floor at the cash entitlement net
        # of CASH income (grant_after_income) so the allowance can never raise
        # the payment above what the recipient would receive with no in-kind at
        # all -- otherwise in-kind would paradoxically increase the benefit when
        # cash income alone already reduced the grant below $59.
        floor = min_(grant_after_income, p.special_allowance.floor)
        return where(
            (in_kind > 0) & (cash_grant < floor),
            floor,
            cash_grant,
        )
