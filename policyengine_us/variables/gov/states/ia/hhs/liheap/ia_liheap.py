from policyengine_us.model_api import *


class ia_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Iowa LIHEAP Regular Assistance"
    documentation = (
        "Annual Iowa Low Income Home Energy Assistance Program Regular "
        "Assistance heating benefit: the per-point amount times total payment "
        "matrix points, between the minimum and maximum benefit, or the flat "
        "deliverable fuel amount for liquid propane and fuel oil households. "
        "The benefit does not depend on the heating bill. Verified for FY2026; "
        "earlier years use model parameter backfilling and are unverified "
        "historical estimates. Crisis assistance, cooling, heating equipment "
        "repair and weatherization are out of scope."
    )
    defined_for = "ia_liheap_eligible"
    reference = (
        # Appendix I, Award Calculation (page 137), Section 11.00 Payments
        # (page 42) and Section 5.41 (page 20).
        "https://hhs.iowa.gov/media/17262/download?inline#page=137",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/IA_BenefitMatrix_Heat-Crisis_2026.pdf#page=1",
        # Section 2.6, minimum $80 and maximum $800.
        "https://liheapch.acf.gov/docs/2026/state-plans/IA_Plan_2026.pdf#page=9",
        # Payment Matrix attachment: flat deliverable fuel amount.
        "https://hhs.iowa.gov/media/16690/download?inline#page=48",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.hhs.liheap.payment
        points = spm_unit("ia_liheap_points", period)
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        # Appendix I: "The minimum Regular Assistance benefit for liquid
        # propane and fuel oil LIHEAP customers is $800"; Section 11.00 raises
        # a lower matrix result "to meet the state-set benefit amount", and the
        # FY26 draft plan calls it "a flat amount ... that serves as both a
        # minimum and maximum benefit for liquid propane and fuel oil". The
        # rule names only those two fuels, so kerosene households receive the
        # matrix amount.
        deliverable_fuel = (heating_type == types.PROPANE) | (
            heating_type == types.FUEL_OIL
        )
        # Appendix I: "$40 per point"; "The minimum benefit an approved LIHEAP
        # customer may receive is $80, and the maximum is $800." Section 5.41:
        # the benefit "is determined by a matrix and does not depend on the
        # actual amount owed by the household", so there is no bill cap.
        matrix_benefit = clip(p.amount_per_point * points, p.min_benefit, p.max_benefit)
        return where(deliverable_fuel, p.deliverable_fuel_amount, matrix_benefit)
