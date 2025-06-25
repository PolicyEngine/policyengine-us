from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_reconciled_qbid() -> Reform:

    class qbi_deduction_component(Variable):
        """
        The preliminary qualified business income (QBI) deduction component for a single
        trade or business under the H.R. 1 proposal. This calculation must be performed
        for each business, and the results are then aggregated and subject to the
        final MTI cap at the filer level.
        """

        value_type = float
        entity = Person
        label = "QBI deduction component for a single business"
        unit = USD
        definition_period = YEAR
        reference = (
            "Description of QBID under the 'One Big Beautiful Bill Act'"
        )

        def formula(person, period, parameters):
            # --------------------------------------------------------------
            # H.R. 1 Qualified Business Income Deduction (QBID) Component
            # This calculates the preliminary deduction (D_pre) for a single business.
            # --------------------------------------------------------------
            p = parameters(period).gov.irs.deductions.qbi
            p_rec = parameters(period).gov.contrib.reconciliation.qbid

            # --- Core Inputs ---------------------------------------------
            # QBI for the specific trade or business
            qbi = person("qualified_business_income", period)

            # Specified Service Trade or Business (SSTB) status
            is_sstb = person("business_is_sstb", period)

            # W-2 wages paid by the business
            w2_wages = person("w2_wages_from_qualified_business", period)

            # Unadjusted Basis Immediately after Acquisition (UBIA) of qualified property
            ubia_property = person(
                "unadjusted_basis_qualified_property", period
            )

            # Person-level inputs from the tax unit
            taxable_income = person.tax_unit(
                "taxable_income_less_qbid", period
            )
            filing_status = person.tax_unit("filing_status", period)

            # --- Parameters from H.R. 1 ---------------------------------
            deduction_rate = p.deduction_rate  # e.g., 0.23 (θ_max)
            ramp_down_rate = p.ramp_down_rate  # e.g., 0.75 (r)
            threshold = p.threshold[filing_status]  # Income threshold (τ)

            # --- Preliminary Deduction Calculation (D_pre) ----------------

            # The base deduction before any limitations.
            # Corresponds to: θ_max * QBI
            base_deduction = deduction_rate * qbi

            # Check if taxable income is above the threshold. The logic differs
            # for taxpayers above and below this threshold.
            is_above_threshold = taxable_income > threshold

            # The logic below matches the formula:
            # D_pre = θ_max * QBI, if T <= τ
            # D_pre = max(S(1)(A), θ_max*QBI - r*(T-τ)), if T > τ and non-SSTB
            # D_pre = max(0, θ_max*QBI - r*(T-τ)), if T > τ and SSTB

            # Step 1: Calculate the wage and capital limitation (S(1)(A) from TCJA).
            # This is only applicable for non-SSTBs above the threshold.
            wage_limit = p.wpa.w2_wages_rate * w2_wages
            capital_limit = (
                p.wpa.w2_wages_alt_rate * w2_wages
                + p.wpa.ubia_rate * ubia_property
            )
            wpa_cap = max_(wage_limit, capital_limit)

            # S(1)(A) is the lesser of the base deduction or the WPA cap.
            # For SSTBs, this limitation path is not available; it is effectively zero.
            s1a_limitation = where(is_sstb, 0, min_(base_deduction, wpa_cap))

            # Step 2: Calculate the ramp-down deduction amount.
            # Corresponds to: max(0, θ_max*QBI - r*(T-τ))
            excess_income = max_(0, taxable_income - threshold)
            ramp_down_amount = p_rec.phase_in_rate * excess_income
            ramp_down_deduction = max_(0, base_deduction - ramp_down_amount)

            # Determine the preliminary deduction (D_pre) by combining the paths.
            # If below threshold, deduction is base_deduction (ramp_down_deduction equals base_deduction).
            # If above threshold:
            #   - For non-SSTB, it's the greater of the S(1)(A) limit or the ramp-down deduction.
            #   - For SSTB, it's just the ramp-down deduction (since s1a_limitation is 0).
            return where(
                is_above_threshold,
                max_(s1a_limitation, ramp_down_deduction),
                base_deduction,
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(qbi_deduction_component)

    return reform


def create_reconciled_qbid_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_reconciled_qbid()

    p = parameters.gov.contrib.reconciliation.qbid

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_reconciled_qbid()
    else:
        return None


reconciled_qbid = create_reconciled_qbid_reform(None, None, bypass=True)
