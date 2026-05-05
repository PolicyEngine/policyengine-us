from policyengine_us.model_api import *


class wa_eceap_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Income-eligible for Washington ECEAP under the standard pathway"
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/RCW/default.aspx?cite=43.216.505",
        "https://www.dcyf.wa.gov/sites/default/files/pdf/eceap/ECEAP-Federal-Poverty-Level-Chart.pdf",
        "https://www.dcyf.wa.gov/sites/default/files/pdf/eceap/State-Median-Income-Chart.pdf",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wa.dcyf.eceap
        spm_unit = person.spm_unit
        income = spm_unit("wa_eceap_family_income", period)
        if p.uses_fpg:
            # 130% FPL ceiling (not 110%): families below 110% FPL have priority
            # for enrollment under RCW 43.216.505, while families between 110%
            # and 130% FPL are allowed for enrollment if space is available
            # under RCW 43.216.512 (no risk factor required). PolicyEngine does
            # not simulate space allocation, so both pathways are treated as
            # eligible. The 130-200% FPL with-risk-factor band is handled in
            # wa_eceap_risk_factor_eligible.
            threshold = spm_unit("spm_unit_fpg", period) * p.income.fpg_rate
        else:
            threshold = spm_unit("hhs_smi", period) * p.income.smi_rate
        return income <= threshold
