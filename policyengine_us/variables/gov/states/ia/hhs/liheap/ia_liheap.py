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
        "deliverable fuel amount for liquid propane and fuel oil (including "
        "kerosene) households that buy the fuel themselves. A household whose "
        "heat is included in its rent receives the matrix amount whatever the "
        "building's fuel. "
        "The benefit does not depend on the heating bill. Verified for FY2026; "
        "earlier years use model parameter backfilling and are unverified "
        "historical estimates. Crisis assistance, cooling, heating equipment "
        "repair and weatherization are out of scope."
    )
    defined_for = "ia_liheap_eligible"
    reference = (
        # Section 5.41, Section 11.00 Payments, Section 12.20 Deliverable Fuel
        # Vendors, Appendix D Energy Burden Table and Appendix I, Award
        # Calculation.
        # PDF pages 20, 42, 47, 122, 137
        "https://hhs.iowa.gov/media/17262/download?inline#page=20",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/IA_BenefitMatrix_Heat-Crisis_2026.pdf#page=1",
        # Section 2.6, minimum $80 and maximum $800.
        "https://liheapch.acf.gov/docs/2026/state-plans/IA_Plan_2026.pdf#page=9",
        # Payment Matrix attachment: flat deliverable fuel amount.
        "https://hhs.iowa.gov/media/16690/download?inline#page=48",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.hhs.liheap.payment
        points = spm_unit("ia_liheap_points", period)
        fuel = spm_unit("ia_liheap_fuel_category", period)
        fuels = fuel.possible_values
        # Appendix I: "The minimum Regular Assistance benefit for liquid
        # propane and fuel oil LIHEAP customers is $800"; Section 11.00 raises
        # a lower matrix result "to meet the state-set benefit amount", and the
        # FY26 draft plan calls it "a flat amount ... that serves as both a
        # minimum and maximum benefit for liquid propane and fuel oil".
        # Appendix I item 3 and the award rule use the same term, "Fuel Oil"
        # (page 137; Section 11.00, page 42). The draft plan (page 48) explains
        # the flat amount by deliverable fuel customers "not being eligible for
        # winter shutoff moratorium protection", and Section 12.20 (page 47)
        # lists kerosene as a deliverable fuel. Kerosene therefore follows fuel
        # oil for both the fuel points and the flat amount; this is an
        # inference, as the manual has no kerosene row.
        deliverable_fuel = (fuel == fuels.PROPANE) | (fuel == fuels.FUEL_OIL)
        # The flat amount is limited to households that buy the deliverable
        # fuel themselves; this is an inference. The draft plan (page 48) ties
        # it to "deliverable fuel customers" and Section 11.00 (page 42) raises
        # "the deliverable fuel benefit". Appendix D (page 122) pays a
        # household whose heat is included in its rent through the electric
        # vendor "because gas usage is indeterminate" or directly, so such a
        # tenant does not buy the fuel and takes the matrix amount, including
        # the heat-in-rent targeting factor.
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        buys_deliverable_fuel = deliverable_fuel & ~heat_in_rent
        # Appendix I: "$40 per point"; "The minimum benefit an approved LIHEAP
        # customer may receive is $80, and the maximum is $800." Section 5.41:
        # the benefit "is determined by a matrix and does not depend on the
        # actual amount owed by the household", so there is no bill cap.
        matrix_benefit = clip(p.amount_per_point * points, p.min_benefit, p.max_benefit)
        return where(buys_deliverable_fuel, p.deliverable_fuel_amount, matrix_benefit)
