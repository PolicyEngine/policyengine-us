from policyengine_us.model_api import *


class me_liheap(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maine LIHEAP total benefit amount"
    definition_period = YEAR
    defined_for = StateCode.ME
    reference = [
        "https://www.mainehousing.org/programs-services/energy/energydetails/liheap",
        "docs/agents/sources/me-liheap/benefit_calculation.md",
        "docs/agents/sources/me-liheap/maine_liheap_overview.md",
        "42 U.S.C. § 8624 - Low Income Home Energy Assistance Program",
    ]

    def formula(spm_unit, period, parameters):
        # Maine LIHEAP provides two types of benefits:
        # 1. Regular heating assistance (available year-round)
        # 2. Crisis assistance (available November - April)

        regular_payment = spm_unit("me_liheap_regular_payment", period)

        # For crisis payment, if period is MONTH, get crisis payment for that month
        # If period is YEAR, crisis payment will be 0 (only available for specific months)
        if period.unit == "month":
            crisis_payment = spm_unit("me_liheap_crisis_payment", period)
        else:
            # For year-level requests, no crisis payment
            # (crisis is only calculated for specific month periods)
            crisis_payment = 0

        # Total LIHEAP benefit is regular payment + any crisis assistance
        # Crisis assistance is additional help during winter months
        return regular_payment + crisis_payment
