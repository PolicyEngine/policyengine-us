from policyengine_us.model_api import *


class ca_marin_general_relief_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = (
        "Eligible for the Marin County General Relief based on the income requirements"
    )
    definition_period = MONTH
    defined_for = "in_marin"
    reference = "https://marin.granicus.com/DocumentViewer.php?file=marin_ce4ed1aaf509aaf7176c360d26f8f1c6.pdf#page=11"

    def formula(spm_unit, period, parameters):
        # Net income is YEAR-defined; reading it at the monthly period
        # auto-divides the annual figure to a monthly amount.
        net_income = spm_unit("ca_marin_general_relief_net_income", period)
        # The Standards require income at or below the maximum cash aid amount.
        # Standards Sec II.I applies "all income received" to applicants and net
        # income to recipients; we apply net income to everyone (matches LA
        # County GR). We don't track GR applicant-vs-recipient status at the moment.
        grant = spm_unit("ca_marin_general_relief_max_grant", period)
        return net_income <= grant
