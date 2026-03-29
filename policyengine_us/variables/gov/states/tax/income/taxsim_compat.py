from policyengine_us.model_api import *


TAXSIM_V32_STATE_AGI_MAPPING = {
    "AL": ["al_agi"],
    "AZ": ["az_agi"],
    "CA": ["ca_agi"],
    "CO": ["adjusted_gross_income"],
    "CT": ["ct_agi"],
    "DC": ["dc_agi"],
    "GA": ["ga_agi"],
    "HI": ["hi_agi"],
    "IA": ["ia_net_income"],
    "ID": ["id_agi"],
    "IL": ["il_base_income"],
    "IN": ["in_agi"],
    "KS": ["ks_agi"],
    "KY": ["ky_agi"],
    "LA": ["la_agi"],
    "MA": ["ma_agi"],
    "MD": ["md_agi"],
    "ME": ["me_agi"],
    "MI": ["adjusted_gross_income"],
    "MN": ["adjusted_gross_income"],
    "MO": ["mo_adjusted_gross_income"],
    "MS": ["ms_agi"],
    "NC": ["adjusted_gross_income"],
    "ND": ["adjusted_gross_income"],
    "NE": ["ne_agi"],
    "NJ": ["nj_agi"],
    "NM": ["nm_modified_gross_income"],
    "NY": ["ny_agi"],
    "OH": ["oh_agi"],
    "OK": ["ok_agi"],
    "OR": ["or_agi"],
    "PA": ["pa_eligibility_income"],
    "RI": ["ri_agi"],
    "UT": ["ut_total_income"],
    "VA": ["va_agi"],
    "VT": ["vt_agi"],
    "WI": ["wi_agi"],
    "WV": ["wv_agi"],
}
TAXSIM_V36_TAXABLE_INCOME_MAPPING = {
    "AL": ["al_taxable_income"],
    "AR": ["ar_taxable_income"],
    "AZ": ["az_taxable_income"],
    "CA": ["ca_taxable_income"],
    "CO": ["co_taxable_income"],
    "CT": ["ct_taxable_income"],
    "DC": ["dc_taxable_income"],
    "DE": ["de_taxable_income"],
    "GA": ["ga_taxable_income"],
    "HI": ["hi_taxable_income"],
    "IA": ["ia_taxable_income"],
    "ID": ["id_taxable_income"],
    "IL": ["il_taxable_income"],
    "IN": ["in_agi"],
    "KS": ["ks_taxable_income"],
    "KY": ["ky_taxable_income"],
    "LA": ["la_taxable_income"],
    "MD": ["md_taxable_income"],
    "ME": ["me_taxable_income"],
    "MI": ["mi_taxable_income"],
    "MN": ["mn_taxable_income"],
    "MO": ["mo_taxable_income"],
    "MS": ["ms_taxable_income"],
    "NC": ["nc_taxable_income"],
    "ND": ["nd_taxable_income"],
    "NE": ["ne_taxable_income"],
    "NH": ["nh_taxable_income"],
    "NJ": ["nj_taxable_income"],
    "NM": ["nm_taxable_income"],
    "NY": ["ny_taxable_income"],
    "OH": ["oh_taxable_income"],
    "OK": ["ok_taxable_income"],
    "OR": ["or_taxable_income"],
    "PA": ["pa_adjusted_taxable_income"],
    "RI": ["ri_taxable_income"],
    "SC": ["sc_taxable_income"],
    "UT": ["ut_taxable_income"],
    "VA": ["va_taxable_income"],
    "VT": ["vt_taxable_income"],
    "WI": ["wi_taxable_income"],
    "WV": ["wv_taxable_income"],
}
TAXSIM_V37_PROPERTY_TAX_CREDIT_MAPPING = {
    "AZ": ["az_property_tax_credit"],
    "CT": ["ct_property_tax_credit"],
    "DC": ["dc_ptc"],
    "MA": ["ma_senior_circuit_breaker"],
    "ME": ["me_property_tax_fairness_credit"],
    "MI": ["mi_homestead_property_tax_credit"],
    "MO": ["mo_property_tax_credit"],
    "MT": ["mt_elderly_homeowner_or_renter_credit"],
    "NJ": ["nj_property_tax_credit"],
    "NM": ["nm_property_tax_rebate"],
    "NY": ["ny_real_property_tax_credit"],
    "RI": ["ri_property_tax_credit"],
    "WI": ["wi_homestead_credit", "wi_property_tax_credit"],
    "WV": ["wv_homestead_excess_property_tax_credit"],
}
TAXSIM_V38_CDCC_MAPPING = {
    "AR": ["ar_cdcc"],
    "CA": ["ca_cdcc"],
    "CO": ["co_cdcc", "co_low_income_cdcc"],
    "DC": ["dc_cdcc", "dc_kccatc"],
    "DE": ["de_cdcc"],
    "GA": ["ga_cdcc"],
    "HI": ["hi_cdcc"],
    "IA": ["ia_cdcc"],
    "KS": ["ks_cdcc"],
    "KY": ["ky_cdcc"],
    "LA": ["la_non_refundable_cdcc", "la_refundable_cdcc"],
    "MA": ["ma_dependent_care_credit"],
    "MD": ["md_cdcc"],
    "ME": ["me_child_care_credit"],
    "MN": ["mn_cdcc"],
    "NE": ["ne_cdcc_nonrefundable", "ne_cdcc_refundable"],
    "NJ": ["nj_cdcc"],
    "NM": ["nm_cdcc"],
    "NY": ["ny_cdcc"],
    "OH": ["oh_cdcc"],
    "OK": ["taxsim_ok_child_care_credit_component"],
    "OR": ["or_working_family_household_and_dependent_care_credit"],
    "PA": ["pa_cdcc"],
    "RI": ["ri_cdcc"],
    "SC": ["sc_cdcc"],
    "VT": ["vt_cdcc", "vt_low_income_cdcc"],
    "WI": ["wi_childcare_expense_credit"],
}
TAXSIM_V39_EITC_MAPPING = {
    "CA": ["ca_eitc"],
    "CO": ["co_eitc"],
    "CT": ["ct_eitc"],
    "DC": ["dc_eitc"],
    "DE": ["de_eitc"],
    "HI": ["hi_eitc"],
    "IA": ["ia_eitc"],
    "IL": ["il_eitc"],
    "IN": ["in_eitc"],
    "KS": ["ks_total_eitc"],
    "LA": ["la_eitc"],
    "MA": ["ma_eitc"],
    "MD": ["md_eitc"],
    "ME": ["me_eitc"],
    "MI": ["mi_eitc"],
    "MN": ["mn_wfc"],
    "MO": ["mo_wftc"],
    "MT": ["mt_eitc"],
    "NE": ["ne_eitc"],
    "NJ": ["nj_eitc"],
    "NM": ["nm_eitc"],
    "NY": ["ny_eitc"],
    "OH": ["oh_eitc"],
    "OK": ["ok_eitc"],
    "OR": ["or_eitc"],
    "RI": ["ri_eitc"],
    "SC": ["sc_eitc"],
    "VA": ["va_eitc"],
    "VT": ["vt_eitc"],
    "WA": ["wa_working_families_tax_credit"],
    "WI": ["wi_earned_income_credit"],
}
TAXSIM_SCTC_MAPPING = {
    "AZ": ["az_dependent_tax_credit"],
    "CA": ["ca_yctc"],
    "CO": ["co_ctc", "co_family_affordability_credit"],
    "CT": ["ct_child_tax_rebate"],
    "DC": ["dc_ctc"],
    "ID": ["id_ctc"],
    "IL": ["il_ctc"],
    "MA": ["ma_child_and_family_credit"],
    "MD": ["md_ctc"],
    "MN": ["taxsim_mn_child_tax_credit_component"],
    "NE": ["ne_refundable_ctc"],
    "NJ": ["nj_ctc"],
    "NM": ["nm_ctc"],
    "NY": ["ny_ctc"],
    "OK": ["taxsim_ok_child_tax_credit_component"],
    "OR": ["or_ctc"],
    "RI": ["ri_child_tax_rebate"],
    "UT": ["ut_ctc"],
    "VT": ["vt_ctc"],
}
TAXSIM_STAXBC_MAPPING = {
    "AL": ["al_income_tax_before_non_refundable_credits"],
    "AR": ["ar_income_tax_before_non_refundable_credits_unit"],
    "AZ": ["az_income_tax_before_non_refundable_credits"],
    "CA": ["ca_income_tax_before_credits"],
    "CO": ["co_income_tax_before_non_refundable_credits"],
    "CT": ["ct_income_tax_before_refundable_credits"],
    "DC": ["dc_income_tax_before_credits"],
    "DE": ["de_income_tax_before_non_refundable_credits_unit"],
    "GA": ["ga_income_tax_before_non_refundable_credits"],
    "HI": ["hi_income_tax_before_non_refundable_credits"],
    "IA": ["ia_income_tax_before_credits"],
    "ID": ["id_income_tax_before_non_refundable_credits"],
    "IL": ["il_income_tax_before_non_refundable_credits"],
    "IN": ["in_income_tax_before_refundable_credits"],
    "KS": ["ks_income_tax_before_credits"],
    "KY": ["ky_income_tax_before_non_refundable_credits_unit"],
    "LA": ["la_income_tax_before_non_refundable_credits"],
    "MA": ["ma_income_tax_before_credits"],
    "MD": ["md_income_tax_before_credits"],
    "ME": ["me_income_tax_before_credits"],
    "MI": ["mi_income_tax_before_non_refundable_credits"],
    "MN": ["mn_income_tax_before_credits"],
    "MO": ["mo_income_tax_before_credits"],
    "MS": ["ms_income_tax_before_credits_unit"],
    "MT": ["mt_income_tax_before_refundable_credits_unit"],
    "NC": ["nc_income_tax_before_credits"],
    "ND": ["nd_income_tax_before_credits"],
    "NE": ["ne_income_tax_before_credits"],
    "NH": ["nh_income_tax_before_refundable_credits"],
    "NJ": ["nj_income_tax_before_refundable_credits"],
    "NM": ["nm_income_tax_before_non_refundable_credits"],
    "NY": ["ny_income_tax_before_credits"],
    "OH": ["oh_income_tax_before_non_refundable_credits"],
    "OK": ["ok_income_tax_before_credits"],
    "OR": ["or_income_tax_before_credits"],
    "PA": ["pa_income_tax"],
    "RI": ["ri_income_tax_before_non_refundable_credits"],
    "SC": ["sc_income_tax_before_non_refundable_credits"],
    "UT": ["ut_income_tax_before_credits"],
    "VA": ["va_income_tax_before_non_refundable_credits"],
    "VT": ["vt_income_tax_before_non_refundable_credits"],
    "WA": ["wa_income_tax_before_refundable_credits"],
    "WI": ["wi_income_tax_before_credits"],
    "WV": ["wv_income_tax_before_non_refundable_credits"],
}


def _state_code(tax_unit, period):
    return tax_unit.household("state_code_str", period)


def _calculate_state_mapped_sum(tax_unit, period, mapping):
    state_code = _state_code(tax_unit, period)
    result = np.zeros_like(tax_unit("adjusted_gross_income", period))

    for code, variables in mapping.items():
        total = add(tax_unit, period, variables)
        result = where(state_code == code, total, result)

    return result


class taxsim_v32_state_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "TAXSIM compatibility state AGI"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        state_code = _state_code(tax_unit, period)
        base = _calculate_state_mapped_sum(
            tax_unit, period, TAXSIM_V32_STATE_AGI_MAPPING
        )
        federal_agi = tax_unit("adjusted_gross_income", period)
        arkansas_agi = max_(
            add(tax_unit, period, ["ar_agi_indiv"]),
            add(tax_unit, period, ["ar_agi_joint"]),
        )
        delaware_agi = max_(
            add(tax_unit, period, ["de_agi_indiv"]),
            add(tax_unit, period, ["de_agi_joint"]),
        )
        montana_agi = tax_unit("state_agi", period)
        uses_federal_agi = np.isin(state_code, ["CO", "MI", "MN", "NC", "ND"])

        result = where(uses_federal_agi, federal_agi, base)
        result = where(state_code == "AR", arkansas_agi, result)
        result = where(state_code == "DE", delaware_agi, result)
        result = where(state_code == "MT", montana_agi, result)
        return where(state_code == "SC", 0, result)


class taxsim_v36_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "TAXSIM compatibility state taxable income"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        state_code = _state_code(tax_unit, period)
        base = _calculate_state_mapped_sum(
            tax_unit, period, TAXSIM_V36_TAXABLE_INCOME_MAPPING
        )
        montana_taxable_income = max_(
            add(tax_unit, period, ["mt_taxable_income_indiv"]),
            add(tax_unit, period, ["mt_taxable_income_joint"]),
        )
        return where(state_code == "MT", montana_taxable_income, base)


class taxsim_v37_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "TAXSIM compatibility state property tax credit"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return _calculate_state_mapped_sum(
            tax_unit, period, TAXSIM_V37_PROPERTY_TAX_CREDIT_MAPPING
        )


class taxsim_v38_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "TAXSIM compatibility state child care credit"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return _calculate_state_mapped_sum(tax_unit, period, TAXSIM_V38_CDCC_MAPPING)


class taxsim_v39_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "TAXSIM compatibility state earned income credit"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return _calculate_state_mapped_sum(tax_unit, period, TAXSIM_V39_EITC_MAPPING)


class taxsim_sctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "TAXSIM compatibility state child tax credit"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return _calculate_state_mapped_sum(tax_unit, period, TAXSIM_SCTC_MAPPING)


class taxsim_staxbc(Variable):
    value_type = float
    entity = TaxUnit
    label = "TAXSIM compatibility state tax before credits"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return _calculate_state_mapped_sum(tax_unit, period, TAXSIM_STAXBC_MAPPING)
