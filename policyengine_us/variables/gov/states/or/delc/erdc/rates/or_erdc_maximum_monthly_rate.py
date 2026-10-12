from policyengine_us.model_api import *


class or_erdc_maximum_monthly_rate(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    unit = USD
    label = "Oregon ERDC maximum monthly provider reimbursement"
    defined_for = "or_erdc_eligible_child"
    reference = (
        "https://secure.sos.state.or.us/oard/view.action?ruleNumber=414-175-0075"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states["or"].delc.erdc
        provider_type = person("or_erdc_provider_type", period)
        area = person("or_erdc_provider_area", period)
        age_group = person("or_erdc_age_group", period)
        hourly_rate = p.rates.hourly[area][provider_type][age_group]
        monthly_rate = p.rates.monthly[area][provider_type][age_group]
        hours = person("or_erdc_monthly_care_hours", period)
        types = provider_type.possible_values
        standard_provider = (provider_type == types.STANDARD_FAMILY) | (
            provider_type == types.STANDARD_CENTER
        )
        # OAR 414-175-0075(3)(a),(b),(e): care below the full-time hours
        # threshold is paid hourly, capped at the full-time monthly rate.
        # The part-time monthly rate in (3)(c) applies only to enhanced or
        # licensed providers that customarily bill all families part-time,
        # and the high needs supplement in OAR 414-175-0076 requires a
        # Department-assessed factor; we track neither provider billing
        # practices nor assessed factors, so both are omitted.
        full_time_hours = where(
            standard_provider,
            p.hours.full_time_threshold.standard,
            p.hours.full_time_threshold.licensed,
        )
        hourly_payment = min_(hourly_rate * hours, monthly_rate)
        return where(hours >= full_time_hours, monthly_rate, hourly_payment)
