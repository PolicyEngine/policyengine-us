from policyengine_us.model_api import *


class in_eap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Indiana EAP regular heating assistance"
    documentation = (
        "Verified for FY2026. Earlier years use model parameter backfilling "
        "and are unverified historical estimates."
    )
    defined_for = "in_eap_eligible"
    reference = "https://www.in.gov/ihcda/files/Indiana-LIHEAP-Intake-and-Operations-Program-Manual-PY2026.pdf#page=10,26,27,32,33,47,69,70,71,72,73,74,75,77,78"

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
        heating_burden = where(
            heat_in_rent, rent_paid, heating_bill & (fuel_points > 0)
        )
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
            | person("receives_ssi", period)
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
