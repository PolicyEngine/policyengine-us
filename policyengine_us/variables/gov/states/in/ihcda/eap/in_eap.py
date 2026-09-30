from policyengine_us.model_api import *


class in_eap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Indiana EAP regular heating assistance"
    defined_for = "in_eap_eligible"
    reference = "https://www.in.gov/ihcda/files/Indiana-LIHEAP-Intake-and-Operations-Program-Manual-PY2026.pdf#page=26,27,32,33,69,70,71,72,73,74,75,77,78"

    def formula_2026(spm_unit, period, parameters):
        # FY2026 is the beginning of researched coverage, not the program's inception.
        p = parameters(period).gov.states["in"].ihcda.eap
        person = spm_unit.members
        smi_amount = spm_unit("in_eap_smi", period)
        quarterly_income = spm_unit("in_eap_income", period) / 4
        low = quarterly_income <= np.floor(smi_amount * p.lower_income_rate / 4)
        middle = quarterly_income <= np.floor(smi_amount * p.middle_income_rate / 4)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        # The shared tenant flag identifies all utilities included in rent. It does not
        # identify electricity alone included in rent while other utilities are separate;
        # that mixed arrangement remains unsupported without an electricity-specific input.
        electric_in_rent = ~spm_unit.household("tenant_pays_utilities", period)
        rent_paid = add(spm_unit, period, ["rent"]) >= p.minimum_monthly_rent * 12
        fuel = spm_unit("heating_type", period)
        fuel_points = p.fuel_points[fuel]
        heating_bill = spm_unit("heating_expense", period) > 0
        heating_burden = where(
            heat_in_rent, rent_paid, heating_bill & (fuel_points > 0)
        )
        income_points = select(
            [heat_in_rent, low, middle],
            [p.higher_income_points, p.lower_income_points, p.middle_income_points],
            default=p.higher_income_points,
        )
        # No existing input identifies site-built, mobile, and multi-unit dwellings.
        # This draft uses the site-built single-family schedule, overestimating mobile
        # homes by $25 and multi-unit homes by $50 when heat is billed separately.
        # Heat included in rent receives zero dwelling and fuel points for every type.
        dwelling_points = where(heat_in_rent, 0, p.single_family_points)
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
            (age >= p.elderly_age)
            | (age <= p.young_child_age_limit)
            | disability
            | person("is_veteran", period)
            | person("is_military", period)
            | (person("current_pregnancies", period) > 0)
        )
        points = (
            income_points
            + dwelling_points
            + fuel_points
            + vulnerable * p.vulnerability_points
        )
        heating = points * p.amount_per_point * heating_burden
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
                    p.higher_income_electric_payment,
                    p.lower_income_electric_payment,
                    p.middle_income_electric_payment,
                ],
                default=p.higher_income_electric_payment,
            )
            * electric_burden
        )
        # Regular awards can create credits and are not capped at the current bill.
        # Existing credit balances, account coding/ownership, unsafe or broken equipment,
        # prior awards and discretionary supplements are not identified by current inputs.
        # Excludes all crisis, cooling, weatherization and equipment payments.
        return heating + electric
