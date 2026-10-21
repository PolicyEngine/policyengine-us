from policyengine_us.model_api import *


class in_eap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Indiana EAP regular heating assistance"
    documentation = (
        "Verified for FY2026. FY2025 uses the PY2024-25 benefit matrix for the "
        "income points, electric payments and fuel points that differ from "
        "FY2026. Its other values, and all earlier years, use model parameter "
        "backfilling and are unverified historical estimates."
    )
    defined_for = "in_eap_eligible"
    reference = (
        # Section 8.11 (page 77) benefit formula, Sections 8.3-8.7 (pages 69-73) points
        # and electric payment, Section 8.8 (pages 73-75), Sections 8.12-8.13 (pages
        # 77-78), Section 1.1 (page 10), Section 3.4 (pages 26-27), Section 4.7 (pages
        # 32-33) and Section 6 (page 47).
        "https://www.in.gov/ihcda/files/Indiana-LIHEAP-Intake-and-Operations-Program-Manual-PY2026.pdf#page=77",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["in"].ihcda.eap
        person = spm_unit.members
        smi_amount = spm_unit("in_eap_smi", period)
        # Sections 6 and 8.3 place a household in an income band using the most recent
        # three months of income, so annual amounts are scaled to that period.
        months_share = p.income.calculation_months / MONTHS_IN_YEAR
        calculation_income = spm_unit("in_eap_income", period) * months_share
        low = calculation_income <= np.floor(
            smi_amount * p.benefit.income.lower_rate * months_share
        )
        middle = calculation_income <= np.floor(
            smi_amount * p.benefit.income.middle_rate * months_share
        )
        # The shared tenant flag identifies all utilities included in rent, so Section
        # 4.7 places both heat and electricity in rent for that household. It does not
        # identify electricity alone included in rent while heat is billed separately;
        # that mixed arrangement remains unsupported without an electricity-specific
        # input.
        electric_in_rent = ~spm_unit.household("tenant_pays_utilities", period)
        heat_in_rent = (
            spm_unit("heat_expense_included_in_rent", period) | electric_in_rent
        )
        rent_paid = (
            add(spm_unit, period, ["rent"])
            >= p.eligibility.minimum_monthly_rent * MONTHS_IN_YEAR
        )
        fuel = spm_unit("heating_type", period)
        fuel_points = p.benefit.fuel_points[fuel]
        heating_bill = spm_unit("heating_expense", period) > 0
        # The fuels that receive the heating award are listed separately from the
        # fuel points: the PY2024-25 matrix gave natural gas and electric heat zero
        # fuel points but still paid the award on the income and dwelling points.
        award_fuel = np.isin(fuel.decode_to_str(), p.benefit.heating_award_fuels)
        heating_burden = where(heat_in_rent, rent_paid, heating_bill & award_fuel)
        income_points = select(
            [heat_in_rent, low, middle],
            [
                p.benefit.income.higher_points,
                p.benefit.income.lower_points,
                p.benefit.income.middle_points,
            ],
            default=p.benefit.income.higher_points,
        )
        dwelling = spm_unit("in_eap_dwelling_type", period)
        # Section 8.4 awards zero dwelling points whenever heat is included in rent.
        dwelling_points = where(heat_in_rent, 0, p.benefit.dwelling_points[dwelling])
        fuel_points = where(heat_in_rent, 0, fuel_points)
        age = person("age", period)
        # Reuse available benefit-receipt evidence. Doctor certification with a pending
        # SSA claim, vocational rehabilitation and black-lung receipt lack exact inputs.
        # Disability with Medicaid receipt approximates the specified Medicaid pathways.
        disability = (
            (person("ssi", period) > 0)
            | (add(person, period, ["receives_ssi"]) > 0)
            | (person("social_security_disability", period) > 0)
            | (person("is_disabled", period) & person("receives_medicaid", period))
        )
        vulnerable = spm_unit.any(
            (age >= p.benefit.vulnerability.elderly_age)
            | (age <= p.benefit.vulnerability.young_child_age_limit)
            | disability
            | person("is_veteran", period)
            | person("is_military", period)
            | (person("current_pregnancies", period) > 0)
        )
        points = (
            income_points
            + dwelling_points
            + fuel_points
            + vulnerable * p.benefit.vulnerability.points
        )
        heating = points * p.benefit.amount_per_point * heating_burden
        # Section 8.7 expressly treats this winter electric allowance as supporting the
        # heating system. Section 8.11 denies it when there is no electric utility service.
        electric_bill = (spm_unit("pre_subsidy_electricity_expense", period) > 0) | (
            (fuel == fuel.possible_values.ELECTRICITY) & heating_bill
        )
        electric_burden = where(electric_in_rent, rent_paid, electric_bill)
        electric = (
            select(
                [electric_in_rent, low, middle],
                [
                    p.benefit.electricity.higher_income,
                    p.benefit.electricity.lower_income,
                    p.benefit.electricity.middle_income,
                ],
                default=p.benefit.electricity.higher_income,
            )
            * electric_burden
        )
        # Regular awards can create credits and are not capped at the current bill.
        # Existing credit balances, account coding/ownership, unsafe or broken equipment,
        # prior awards and discretionary supplements are not identified by current inputs.
        # Excludes all crisis, cooling, weatherization and equipment payments.
        return heating + electric
