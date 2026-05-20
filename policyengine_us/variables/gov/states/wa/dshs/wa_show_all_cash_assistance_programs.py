from policyengine_us.model_api import *


class wa_show_all_cash_assistance_programs(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Treat all Washington cash assistance programs as immigration-eligible for display"
    definition_period = MONTH
    defined_for = StateCode.WA
    # WARNING: DISPLAY-ONLY FLAG. Set this to True ONLY in consumer-facing
    # contexts (e.g., a benefit-eligibility tool that needs to show TANF,
    # SFA, and RCA amounts side by side for the same household). It bypasses
    # the immigration-based mutual exclusivity that normally makes these
    # three cash-assistance programs disjoint.
    #
    # MUST NOT be set to True for microsimulation, aggregate measures, or
    # any computation that flows into spm_unit_benefits / household_net_income.
    # Doing so triple-counts cash assistance, since wa_tanf, wa_sfa, and
    # wa_rca all become payable for the same unit and all three feed into
    # spm_unit_benefits.
    #
    # If a consumer of this flag must compute aggregates while the flag is
    # set, it should explicitly zero out the redundant programs (e.g., keep
    # only the highest-priority program among TANF/SFA/RCA per unit) or
    # toggle this flag back to False before reading aggregate outputs.
    # Does not override demographic, income, or resource tests.
