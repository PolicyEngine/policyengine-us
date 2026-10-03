# Hawaii regular heating components

These FY2026 components implement qualified household size, annualized countable
income, the percentage-based income ceiling, private-dwelling points and the
published subsidized-dwelling amount schedule. They do not determine final
eligibility or a dollar award. The statewide value per point is not published in
the acquired sources: $140 is explicitly an example. No hypothetical value is
encoded. Full regular heating assistance remains incomplete.

Gas EC is heating; electricity EC is cooling and outside this task. Household
SPM membership approximates the unit sharing utilities. All members' income,
including minor earnings and income of nonqualified members, counts, but only
qualified members count toward the size schedule. COFA status needs an explicit
qualified-member boolean because the shared immigration enum lacks that status.
Historical household rules are corroborated by the current application.

Annual income and electric expenses approximate the prior-month assessment.
Existing net business inputs need no second deduction. Pension, Social Security
and retirement-distribution aggregates are counted once, with separate private
survivor receipts. Monthly SSI and state TANF are annualized; TANF enters once
per household. No Medicare adjustment is added. Cash gifts from friends or relatives enter through financial_assistance, and
lottery/gambling winnings enter through gambling_winnings. Mortgage principal
receipts, jury compensation, settlements, foster/adoption payments and community
service stipends lack separately identified inputs. Wage-embedded work-study,
VA education payments and earmarked insurance reimbursements cannot be reliably
separated. Those are missing facts, not policy exclusions; life insurance
receipts are included as represented lump-sum insurance proceeds.

The adopted percentage income limits use requested-year SMI and prior-calendar-
year Hawaii FPG. The matrix labels its income dollar table as projected and has
an inconsistent six-person cell. The model does not copy that error or assert
that all projected dollar cells follow a uniform rounding rule. Final threshold
inclusivity and the categorical mandatory-member case condition still need
resolution before an eligibility award is introduced.

Private dwelling points follow the adopted plan's age-five-inclusive language.
Disability counts for adults. Burden uses electric expenses even for gas aid,
consistent with the historical manual and current application. Positive expense
at zero income is treated as high burden, but zero expense does not earn that
point. County maps Oahu to Honolulu. Explicit unknown county earns zero regional
points; omitted county retains the shared model first-county fallback.
Points are before eligibility and housing dispatch, and are not a benefit.
The flat schedule likewise does not assert that its recipient meets eligibility.
Photovoltaic net consumption cannot be inferred from solar heating type.

Parameters are verified for FY2026 only after tests. Earlier backfilled results
are unverified historical estimates. FY2027 sources are proposed, not adopted.
Crisis, cooling, weatherization and equipment are outside this work.

Sources are recorded in the individual variable and parameter references and
the Wave2C source manifest, which preserves the accepted plan, published matrix,
historical manual, current application and draft documents separately.
