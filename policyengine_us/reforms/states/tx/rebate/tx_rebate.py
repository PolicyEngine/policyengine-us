"""Texas "Money in Your Pocket" one-time rebate reform.

Proposal: Gina Hinojosa's "Money in Your Pocket" economic agenda proposes a
one-time $1,500 rebate check to Texas families, funded by an ~$17 billion draw
on the state's Economic Stabilization Fund.
Source: https://ginafortexas.com/2026/07/recap-gina-hinojosa-launches-money-in-your-pocket-economic-agenda-across-houston-san-antonio-and-laredo/

Modeling assumptions: the proposal does not specify the eligibility unit or an
income limit. PolicyEngine models one check per household with no income limit --
the reading consistent with the campaign's stated ~$17 billion Economic
Stabilization Fund draw. The campaign's "families" are therefore operationalized
as households. The rebate is paid once (2027) and reverts to $0 from 2028.
"""

from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_tx_rebate() -> Reform:
    class tx_rebate(Variable):
        value_type = float
        entity = Household
        label = "Texas rebate check"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.TX
        reference = "https://ginafortexas.com/2026/07/recap-gina-hinojosa-launches-money-in-your-pocket-economic-agenda-across-houston-san-antonio-and-laredo/"

        def formula(household, period, parameters):
            return parameters(period).gov.contrib.states.tx.rebate.amount

    def modify_parameters(parameters):
        state_benefits = parameters.gov.household.household_state_benefits
        current_benefits = state_benefits(instant("2027-01-01"))
        if "tx_rebate" not in current_benefits:
            new_benefits = list(current_benefits) + ["tx_rebate"]
            state_benefits.update(
                start=instant("2027-01-01"),
                stop=instant("2027-12-31"),
                value=new_benefits,
            )
        return parameters

    class spm_unit_benefits(Variable):
        value_type = float
        entity = SPMUnit
        label = "Benefits"
        definition_period = YEAR
        unit = USD

        def formula(spm_unit, period, parameters):
            BENEFITS = [
                "social_security",
                "ssi",
                "in_ssp",
                "ct_ssp",
                "ga_ssp",
                "al_ssp",
                "ak_ssp",
                "dc_ossp",  # DC benefits
                "id_aabd",  # Idaho benefits
                "ky_ssp",  # Kentucky benefits
                "de_ssp",  # Delaware benefits
                "fl_oss",
                "ks_sspp",  # Kansas benefits
                "hi_oss",
                "la_oss",  # Louisiana benefits
                "ma_state_supplement",  # Massachusetts benefits
                "md_paa",  # Maryland benefits
                "wa_ssp",  # Washington benefits
                "mi_ssp",  # Michigan benefits
                "me_ssp",  # Maine benefits
                "mo_ssp",  # Missouri benefits
                "mn_msa",  # Minnesota benefits
                "ne_aabd",  # Nebraska benefits
                # California programs.
                "ca_cvrp",  # California Clean Vehicle Rebate Project.
                # Colorado programs.
                "co_ccap_subsidy",
                "co_state_supplement",
                "co_oap",
                # Washington programs.
                "wa_child_care_subsidies",
                # New Mexico programs.
                "nm_ssi_state_supplement",
                # South Carolina programs.
                "sc_ssi_state_supplement",
                # Texas programs.
                "tx_ssi_state_supplement",
                # West Virginia programs.
                "wv_child_care_subsidies",
                "snap",
                "wic",
                "free_school_meals",
                "reduced_price_school_meals",
                "child_support_received",
                "workers_compensation",
                "educational_assistance",
                "financial_assistance",
                "survivor_benefits",
                "spm_unit_energy_subsidy",
                "tanf",
                # Washington (WA) cash-assistance programs. wa_sfa and wa_rca
                # sit alongside the federal TANF aggregator entry; under default
                # rules these three are mutually exclusive at the SPM-unit level
                # so summing them does not double-count.
                "wa_sfa",
                "wa_rca",
                "high_efficiency_electric_home_rebate",
                "residential_efficiency_electrification_rebate",
                "unemployment_compensation",
                # One-time energy relief payments.
                # Paid at the same time as the Alaska Permanent Fund Dividend,
                # which is part of IRS gross income.
                "ak_energy_relief",
                # Contributed.
                "basic_income",
                "ny_drive_clean_rebate",
                "tx_rebate",
            ]
            if parameters(period).gov.contrib.ubi_center.flat_tax.deduct_ptc:
                BENEFITS.append("assigned_aca_ptc")
            if not parameters(period).gov.hud.abolition:
                BENEFITS.append("spm_unit_capped_housing_subsidy")
            return add(spm_unit, period, BENEFITS)

    class reform(Reform):
        def apply(self):
            self.update_variable(tx_rebate)
            self.update_variable(spm_unit_benefits)
            self.modify_parameters(modify_parameters)

    return reform


def create_tx_rebate_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_tx_rebate()

    p = parameters.gov.contrib.states.tx.rebate

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_tx_rebate()
    else:
        return None


tx_rebate = create_tx_rebate_reform(None, None, bypass=True)
