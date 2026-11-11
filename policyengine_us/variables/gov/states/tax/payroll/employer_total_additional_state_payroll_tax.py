from policyengine_us.model_api import *


class employer_total_additional_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Employer total additional state payroll taxes and contributions"
    documentation = (
        "Employer-level state payroll taxes and contributions other than "
        "state unemployment insurance, from aggregate employer inputs. For "
        "programs where the law caps the employer's deduction from wages and "
        "the employer pays what it does not deduct, it applies the person's "
        "state_payroll_premium_deduction_share to the whole payroll, as if "
        "the employer deducts the same share for everyone."
    )
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        state_code = person.household("state_code", period)
        headcount = person("employer_headcount", period)
        ss_taxable = person(
            "employer_total_taxable_earnings_for_social_security", period
        )
        # Where the law caps the employer's deduction from wages, the employer
        # pays the part of the permitted employee share it does not deduct.
        deducted = person("state_payroll_premium_deduction_share", period)
        state_ui_taxable = person(
            "employer_total_taxable_earnings_for_state_unemployment_tax", period
        )

        ca = (
            parameters(
                period
            ).gov.states.ca.tax.payroll.employment_training.employer_rate
            * state_ui_taxable
        )

        co_p = parameters(period).gov.states.co.tax.payroll.famli
        co_wages = person("employer_total_co_famli_taxable_wages", period)
        co = (
            where(
                headcount >= co_p.employer_headcount_threshold,
                co_p.employer_rate * co_wages,
                0,
            )
            + (1 - deducted) * co_p.employee_rate * co_wages
        )

        dc = parameters(
            period
        ).gov.states.dc.tax.payroll.paid_leave.employer_rate * person(
            "employer_total_dc_paid_leave_taxable_wages", period
        )

        de_p = parameters(period).gov.states.de.tax.payroll.paid_leave
        de_full_coverage_rate = (
            de_p.family_caregiver_rate + de_p.medical_rate + de_p.parental_rate
        )
        de_contribution_rate = select(
            [
                headcount < de_p.small_employer_threshold,
                headcount < de_p.full_coverage_threshold,
            ],
            [0, de_p.parental_rate],
            default=de_full_coverage_rate,
        )
        de = de_contribution_rate * (1 - de_p.employee_share * deducted) * ss_taxable

        ma_p = parameters(period).gov.states.ma.tax.payroll.paid_leave
        ma_wages = person("employer_total_ma_paid_leave_taxable_wages", period)
        ma_employer_rate = ma_p.family_rate * (
            1 - ma_p.family_employee_share
        ) + ma_p.medical_rate * (1 - ma_p.medical_employee_share)
        ma_employee_rate = (
            ma_p.family_rate * ma_p.family_employee_share
            + ma_p.medical_rate * ma_p.medical_employee_share
        )
        ma = (
            where(
                headcount >= ma_p.employer_headcount_threshold,
                ma_employer_rate * ma_wages,
                0,
            )
            + (1 - deducted) * ma_employee_rate * ma_wages
        )

        me_p = parameters(period).gov.states.me.tax.payroll.paid_leave
        me_wages = person("employer_total_me_paid_leave_taxable_wages", period)
        me = (
            where(
                headcount >= me_p.employer_headcount_threshold,
                me_p.employer_rate * me_wages,
                0,
            )
            + (1 - deducted) * me_p.employee_rate * me_wages
        )

        # The premium and permitted employee rates depend on the small
        # employer test (Minn. Stat. 268B.14, subd. 5a), which reads the same
        # employer inputs as the per-worker path.
        mn = (
            person("mn_paid_leave_premium_rate", period)
            - deducted * person("mn_paid_leave_permitted_employee_rate", period)
        ) * person("employer_total_mn_paid_leave_taxable_wages", period)

        or_p = parameters(period).gov.states["or"].tax.payroll.paid_leave
        or_tax = where(
            headcount >= or_p.employer_headcount_threshold,
            or_p.employer_rate
            * person("employer_total_or_paid_leave_taxable_wages", period),
            0,
        )

        ri = (
            parameters(
                period
            ).gov.states.ri.tax.payroll.job_development_fund.employer_rate
            * state_ui_taxable
        )

        vt_p = parameters(period).gov.states.vt.tax.payroll.child_care
        vt = (vt_p.employer_rate + (1 - deducted) * vt_p.employee_rate) * person(
            "employer_total_vt_child_care_contribution_wages", period
        )

        wa_p = parameters(period).gov.states.wa.tax.payroll.paid_leave
        wa_wages = person("employer_total_wa_paid_leave_taxable_wages", period)
        wa = (
            where(
                headcount >= wa_p.employer_headcount_threshold,
                wa_p.total_rate * wa_p.employer_share * wa_wages,
                0,
            )
            + (1 - deducted) * wa_p.total_rate * (1 - wa_p.employer_share) * wa_wages
        )

        return select(
            [
                state_code == StateCode.CA,
                state_code == StateCode.CO,
                state_code == StateCode.DC,
                state_code == StateCode.DE,
                state_code == StateCode.MA,
                state_code == StateCode.ME,
                state_code == StateCode.MN,
                state_code == StateCode.OR,
                state_code == StateCode.RI,
                state_code == StateCode.VT,
                state_code == StateCode.WA,
            ],
            [ca, co, dc, de, ma, me, mn, or_tax, ri, vt, wa],
            default=0,
        )
