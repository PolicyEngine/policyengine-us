from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.il.dhs.ccap.rates.il_ccap_provider_type import (
    ILCCAPProviderType,
)


class il_ccap_max_monthly_reimbursement(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = MONTH
    label = "Illinois CCAP maximum monthly base reimbursement per child"
    defined_for = "il_ccap_eligible_child"
    reference = (
        "https://www.dhs.state.il.us/page.aspx?item=10864",
        "https://www.dhs.state.il.us/onenetlibrary/12/documents/Forms/444708-202512_REV1.pdf#page=1",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.dhs.ccap.rates
        daily_rate = person("il_ccap_max_daily_rate", period)
        eligible_child = person("il_ccap_eligible_child", period)
        attending_days = max_(
            person("childcare_attending_days_per_month", period.this_year),
            0,
        )
        approved_days = max_(
            person("il_ccap_approved_eligible_days_per_month", period),
            0,
        )
        provider_type = person("il_ccap_provider_type", period)
        home_provider = (provider_type == ILCCAPProviderType.LICENSED_HOME) | (
            provider_type == ILCCAPProviderType.LICENSE_EXEMPT_HOME
        )
        home_eligible_child = home_provider & eligible_child
        family_attending_days = person.spm_unit.sum(
            attending_days * home_eligible_child
        )
        family_approved_days = person.spm_unit.sum(approved_days * home_eligible_child)
        attendance_rate = np.divide(
            family_attending_days,
            family_approved_days,
            out=np.zeros_like(family_attending_days, dtype=float),
            where=family_approved_days > 0,
        )
        eligible_days_payable = (
            home_provider
            & (attendance_rate >= p.attendance.threshold)
            & (attending_days > 0)
        )
        payable_days = where(
            eligible_days_payable,
            max_(approved_days, attending_days),
            attending_days,
        )
        return daily_rate * payable_days
