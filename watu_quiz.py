import streamlit as st

st.set_page_config(
    page_title="Senior Data Analytics Practice Quiz",
    page_icon="🏦",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d6a9f 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
        text-align: center;
    }
    .q-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .cat-pill {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .pill-SQL       { background:#E6F1FB; color:#0C447C; }
    .pill-Python    { background:#EEEDFE; color:#3C3489; }
    .pill-PowerBI   { background:#EAF3DE; color:#27500A; }
    .pill-Stats     { background:#FAEEDA; color:#633806; }
    .pill-Scenario  { background:#FAECE7; color:#712B13; }
    .diff-hard      { background:#FCEBEB; color:#791F1F; padding:2px 8px; border-radius:6px; font-size:0.75rem; }
    .diff-medium    { background:#FAEEDA; color:#633806; padding:2px 8px; border-radius:6px; font-size:0.75rem; }
    .diff-easy      { background:#EAF3DE; color:#27500A; padding:2px 8px; border-radius:6px; font-size:0.75rem; }
    .expl-box {
        border-left: 4px solid #1D9E75;
        background: #f0faf5;
        padding: 0.85rem 1rem;
        border-radius: 0 8px 8px 0;
        font-size: 0.9rem;
        color: #2c2c2c;
        margin-top: 0.75rem;
    }
    .score-card {
        background: #EBF5FB;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stButton > button {
        border-radius: 8px;
        font-size: 0.9rem;
    }
    div[data-testid="stHorizontalBlock"] { gap: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# ── Question Bank ─────────────────────────────────────────────────────────────
QUESTIONS = [
    {
        "cat": "SQL", "diff": "medium",
        "q": "The Company's loans table stores every loan issued to a client. Write a query to find all clients who currently have more than one active loan, showing their client_id and total outstanding balance.",
        "code": """-- loans(loan_id, client_id, disbursement_date,
--   outstanding_balance, status)
-- status values: 'active', 'closed', 'defaulted'""",
        "opts": [
            "SELECT client_id,\n  COUNT(*) AS active_loans,\n  SUM(outstanding_balance) AS total_outstanding\nFROM loans\nWHERE status = 'active'\nGROUP BY client_id\nHAVING COUNT(*) > 1",
            "SELECT client_id, SUM(outstanding_balance)\nFROM loans\nGROUP BY client_id\nHAVING COUNT(*) > 1",
            "SELECT DISTINCT client_id FROM loans\nWHERE outstanding_balance > 0",
            "SELECT client_id, MAX(outstanding_balance)\nFROM loans WHERE status = 'active'\nGROUP BY client_id",
        ],
        "ans": 0,
        "expl": "WHERE status = 'active' filters before aggregation, ensuring only active loans are counted. HAVING COUNT(*) > 1 then restricts to clients with multiple active loans. Option B is missing the status filter — it would include closed and defaulted loans in the count.",
    },
    {
        "cat": "SQL", "diff": "hard",
        "q": "The Company wants to identify clients who missed a repayment in the previous calendar month. Write a query using the repayments and schedules tables.",
        "code": """-- schedules(schedule_id, loan_id, client_id, due_date, expected_amount)
-- repayments(repayment_id, loan_id, client_id, payment_date, amount_paid)""",
        "opts": [
            "SELECT DISTINCT s.client_id\nFROM schedules s\nLEFT JOIN repayments r\n  ON s.loan_id = r.loan_id\n  AND DATE_TRUNC('month', r.payment_date) = DATE_TRUNC('month', s.due_date)\nWHERE DATE_TRUNC('month', s.due_date)\n  = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')\nAND r.repayment_id IS NULL",
            "SELECT client_id FROM repayments\nWHERE amount_paid = 0",
            "SELECT client_id FROM schedules\nWHERE due_date < CURRENT_DATE",
            "SELECT client_id FROM schedules\nGROUP BY client_id HAVING COUNT(*) > 1",
        ],
        "ans": 0,
        "expl": "A LEFT JOIN keeps all scheduled payments, then r.repayment_id IS NULL identifies those with no matching repayment. The date filter scopes to the previous calendar month. This is the correct pattern for detecting missed obligations — a plain WHERE on repayments would miss clients who never paid at all.",
    },
    {
        "cat": "SQL", "diff": "hard",
        "q": "Calculate the Portfolio at Risk (PAR30) for The Company: the percentage of the outstanding portfolio where any scheduled payment is more than 30 days overdue.",
        "code": """-- loans(loan_id, client_id, outstanding_balance, status)
-- schedules(schedule_id, loan_id, due_date, expected_amount)
-- PAR30 = outstanding balance of at-risk loans / total outstanding""",
        "opts": [
            "SELECT\n  SUM(CASE WHEN l.loan_id IN (\n    SELECT loan_id FROM schedules\n    WHERE due_date < CURRENT_DATE - 30\n    AND schedule_id NOT IN (\n      SELECT schedule_id FROM repayments\n      WHERE amount_paid >= expected_amount)\n  ) THEN outstanding_balance ELSE 0 END)\n  / NULLIF(SUM(outstanding_balance), 0) AS par30\nFROM loans\nWHERE status = 'active'",
            "SELECT COUNT(*) / COUNT(DISTINCT client_id)\nFROM loans WHERE status = 'defaulted'",
            "SELECT AVG(outstanding_balance) FROM loans\nWHERE outstanding_balance > 0",
            "SELECT SUM(expected_amount) FROM schedules\nWHERE due_date < CURRENT_DATE",
        ],
        "ans": 0,
        "expl": "PAR30 requires identifying loans with at least one overdue unpaid instalment, then summing their outstanding balances as a ratio of the total active portfolio. NULLIF(..., 0) prevents division-by-zero. This is a standard microfinance KPI — knowing this formula is expected at senior level.",
    },
    {
        "cat": "SQL", "diff": "medium",
        "q": "The Company wants a month-by-month count of new client acquisitions and cumulative total clients. Which query is correct?",
        "code": "-- clients(client_id, registration_date, branch_id)",
        "opts": [
            "SELECT\n  DATE_TRUNC('month', registration_date) AS month,\n  COUNT(*) AS new_clients,\n  SUM(COUNT(*)) OVER\n    (ORDER BY DATE_TRUNC('month', registration_date)) AS cumulative_clients\nFROM clients\nGROUP BY 1\nORDER BY 1",
            "SELECT registration_date,\n  COUNT(*) AS new_clients\nFROM clients GROUP BY registration_date",
            "SELECT client_id, COUNT(*)\nFROM clients GROUP BY client_id",
            "SELECT COUNT(DISTINCT client_id) FROM clients",
        ],
        "ans": 0,
        "expl": "SUM(COUNT(*)) OVER (ORDER BY month) is a nested window function — the inner COUNT(*) aggregates per month, then SUM runs a cumulative total over those monthly counts. This is a common senior-level pattern. DATE_TRUNC groups daily dates into monthly buckets correctly.",
    },
    {
        "cat": "SQL", "diff": "hard",
        "q": "For each branch of The Company, find the loan officer with the highest repayment collection rate. Return branch_id, officer_id, and their collection rate.",
        "code": """-- loans(loan_id, officer_id, branch_id, expected_total)
-- repayments(repayment_id, loan_id, amount_paid)""",
        "opts": [
            "SELECT branch_id, officer_id, collection_rate FROM (\n  SELECT\n    l.branch_id, l.officer_id,\n    SUM(r.amount_paid) / NULLIF(SUM(l.expected_total),0) AS collection_rate,\n    RANK() OVER (\n      PARTITION BY l.branch_id\n      ORDER BY SUM(r.amount_paid)/NULLIF(SUM(l.expected_total),0) DESC\n    ) AS rnk\n  FROM loans l\n  LEFT JOIN repayments r ON l.loan_id = r.loan_id\n  GROUP BY l.branch_id, l.officer_id\n) t WHERE rnk = 1",
            "SELECT officer_id, MAX(amount_paid)\nFROM repayments GROUP BY officer_id",
            "SELECT branch_id, COUNT(officer_id)\nFROM loans GROUP BY branch_id",
            "SELECT officer_id FROM loans\nORDER BY expected_total DESC LIMIT 1",
        ],
        "ans": 0,
        "expl": "The subquery aggregates collection rates per officer per branch, then RANK() OVER (PARTITION BY branch_id) ranks within each branch. Filtering WHERE rnk = 1 returns the top officer per branch. LEFT JOIN ensures officers with zero collections are included (rate = 0, not excluded).",
    },
    {
        "cat": "Python", "diff": "medium",
        "q": "You receive The Company's daily repayment file as an Excel sheet. The 'payment_date' column has mixed formats: some rows are '2024-03-15', others are '15/03/2024'. How do you handle this safely in pandas?",
        "code": """import pandas as pd
df = pd.read_excel('daily_repayments.xlsx')
# payment_date dtype: object""",
        "opts": [
            "df['payment_date'] = pd.to_datetime(\n  df['payment_date'],\n  dayfirst=True,\n  errors='coerce'\n)",
            "df['payment_date'] = df['payment_date'].astype('datetime64')",
            "df['payment_date'] = pd.to_datetime(df['payment_date'])",
            "df['payment_date'] = df['payment_date'].apply(str)",
        ],
        "ans": 0,
        "expl": "dayfirst=True handles the DD/MM/YYYY format, and errors='coerce' converts any unparseable values to NaT instead of crashing. Without dayfirst, '15/03/2024' would raise an error or be misinterpreted. Option C with no arguments would fail on ambiguous or non-standard formats.",
    },
    {
        "cat": "Python", "diff": "hard",
        "q": "The Company's client dataset has duplicate client_id rows because of a system migration. Some duplicates have different values in 'phone_number'. Write code to deduplicate, keeping the most recently updated record per client.",
        "code": """import pandas as pd
df = pd.read_excel('clients.xlsx')
# columns: client_id, name, phone_number, last_updated (datetime)""",
        "opts": [
            "df['last_updated'] = pd.to_datetime(df['last_updated'])\ndf = (\n  df.sort_values('last_updated', ascending=False)\n  .drop_duplicates(subset='client_id', keep='first')\n  .reset_index(drop=True)\n)",
            "df = df.drop_duplicates(subset='client_id')",
            "df = df.dropna(subset=['client_id'])",
            "df = df.groupby('client_id').first().reset_index()",
        ],
        "ans": 0,
        "expl": "Sorting descending by last_updated then drop_duplicates(keep='first') retains the most recent row per client. Option B keeps an arbitrary first occurrence, potentially old data. Option D uses .first() which picks the first row in group order, not the most recent — unless sorted first.",
    },
    {
        "cat": "Python", "diff": "hard",
        "q": "You need to calculate each client's days past due (DPD) for The Company — the number of days since their earliest unpaid scheduled payment.",
        "code": """import pandas as pd
from datetime import date
df = pd.read_excel('schedules.xlsx')
# columns: client_id, due_date, paid (bool)""",
        "opts": [
            "today = pd.Timestamp.today().normalize()\nunpaid = df[df['paid'] == False].copy()\nunpaid['due_date'] = pd.to_datetime(unpaid['due_date'])\ndpd = (\n  unpaid.groupby('client_id')['due_date']\n  .min()\n  .reset_index()\n)\ndpd['dpd'] = (today - dpd['due_date']).dt.days",
            "dpd = df.groupby('client_id')['due_date'].max()",
            "dpd = (pd.Timestamp.today() - df['due_date']).dt.days",
            "dpd = df[df['paid']==False]['due_date'].mean()",
        ],
        "ans": 0,
        "expl": "DPD is measured from the earliest unpaid instalment, not the latest. Filtering to unpaid rows first, then grouping by client_id and taking .min() of due_date gives the oldest missed payment. Subtracting today gives the number of days overdue. Option B uses .max() — that would underestimate delinquency.",
    },
    {
        "cat": "Python", "diff": "medium",
        "q": "The Company's loan portfolio file has an 'interest_rate' column stored as strings like '18%' and '21.5%'. Convert this column to a usable float (as a decimal, e.g. 0.18).",
        "code": """import pandas as pd
df = pd.read_excel('portfolio.xlsx')
# interest_rate: '18%', '21.5%', '15%'""",
        "opts": [
            "df['interest_rate'] = (\n  df['interest_rate']\n  .str.replace('%', '', regex=False)\n  .astype(float) / 100\n)",
            "df['interest_rate'] = df['interest_rate'].astype(float)",
            "df['interest_rate'] = float(df['interest_rate'])",
            "df['interest_rate'] = df['interest_rate'].str[:-1]",
        ],
        "ans": 0,
        "expl": ".str.replace('%', '') strips the percent symbol, .astype(float) converts to number, then dividing by 100 gives the decimal rate (0.18 not 18). Option B raises ValueError because '18%' cannot be directly cast to float. Option D strips the last character but leaves a string — not a numeric type.",
    },
    {
        "cat": "Power BI", "diff": "medium",
        "q": "In The Company's Power BI dashboard, you need a measure that shows the repayment collection rate: total amount collected divided by total amount scheduled, within the current filter context.",
        "code": """-- Tables:
-- Repayments[amount_paid]
-- Schedules[expected_amount]""",
        "opts": [
            "Collection Rate =\nDIVIDE(\n  SUM(Repayments[amount_paid]),\n  SUM(Schedules[expected_amount])\n)",
            "Collection Rate =\n  SUM(Repayments[amount_paid]) /\n  SUM(Schedules[expected_amount])",
            "Collection Rate =\n  AVERAGE(Repayments[amount_paid])",
            "Collection Rate =\n  COUNTROWS(Repayments) / COUNTROWS(Schedules)",
        ],
        "ans": 0,
        "expl": "DIVIDE() is always preferred in DAX over the / operator because it safely returns BLANK (not an error) when the denominator is zero. This is critical for branches or periods with no scheduled amounts. Option B would throw a division-by-zero error in those cases, breaking the visual.",
    },
    {
        "cat": "Power BI", "diff": "hard",
        "q": "The Company's leadership wants to see loan disbursements compared to the same month last year (SPLY) in a single visual. Write the correct DAX measure.",
        "code": """-- DateTable[Date] is a marked date table
-- Loans[amount] is the disbursement amount""",
        "opts": [
            "SPLY Disbursements =\nCALCULATE(\n  SUM(Loans[amount]),\n  SAMEPERIODLASTYEAR(DateTable[Date])\n)",
            "SPLY Disbursements = SUM(Loans[amount]) - 12",
            "SPLY Disbursements =\n  CALCULATE(SUM(Loans[amount]),\n    DATEADD(DateTable[Date], -12, MONTH))",
            "SPLY Disbursements =\n  SUM(Loans[amount]) / PREVIOUSYEAR(DateTable[Date])",
        ],
        "ans": 0,
        "expl": "SAMEPERIODLASTYEAR() is a time intelligence function that returns the same period in the prior year — matching the current filter context exactly (e.g. if March 2024 is selected, it returns March 2023). Option C using DATEADD(-12, MONTH) also works but is less readable. Both require a marked DateTable.",
    },
    {
        "cat": "Power BI", "diff": "hard",
        "q": "A report for The Company has a branch slicer. You need a card visual that always shows the national PAR30 regardless of which branch is selected. What DAX pattern achieves this?",
        "code": """-- Loans[outstanding_balance], Loans[branch_id]
-- Loans[is_par30] (1 if PAR30, 0 otherwise)""",
        "opts": [
            "National PAR30 =\nCALCULATE(\n  DIVIDE(\n    SUMX(ALL(Loans), Loans[is_par30] * Loans[outstanding_balance]),\n    SUMX(ALL(Loans), Loans[outstanding_balance])\n  )\n)",
            "National PAR30 =\n  SUM(Loans[is_par30]) / COUNT(Loans[loan_id])",
            "National PAR30 =\n  CALCULATE(SUM(Loans[outstanding_balance]),\n    Loans[is_par30] = 1)",
            "National PAR30 = AVERAGE(Loans[is_par30])",
        ],
        "ans": 0,
        "expl": "ALL(Loans) inside CALCULATE removes all filters including the branch slicer, ensuring the calculation always uses the full national portfolio. SUMX iterates each row to compute the weighted ratio. Option C returns only the at-risk balance, not a rate, and is still affected by the slicer.",
    },
    {
        "cat": "Power BI", "diff": "medium",
        "q": "The Company's dashboard has a date slicer. You need a measure showing loans active AS OF the selected date, not just loans disbursed on that date. Which DAX is correct?",
        "code": """-- Loans[disbursement_date], Loans[maturity_date]
-- DateTable[Date]""",
        "opts": [
            "Active Loans As Of Date =\nCALCULATE(\n  COUNTROWS(Loans),\n  Loans[disbursement_date] <= MAX(DateTable[Date]),\n  Loans[maturity_date] >= MAX(DateTable[Date])\n)",
            "Active Loans As Of Date = COUNTROWS(Loans)",
            "Active Loans As Of Date = COUNT(Loans[disbursement_date])",
            "Active Loans As Of Date =\n  CALCULATE(COUNTROWS(Loans),\n    DateTable[Date] = TODAY())",
        ],
        "ans": 0,
        "expl": "A loan is active on a given date if it was disbursed on or before that date AND matures on or after that date. Using MAX(DateTable[Date]) captures the selected date from the slicer context. This is a common senior Power BI pattern for point-in-time portfolio snapshots.",
    },
    {
        "cat": "Statistics", "diff": "medium",
        "q": "The Company pilots a new credit scoring model in one region. Default rate drops from 18% to 14%. p-value = 0.03, alpha = 0.05, n = 800 clients. What is the correct conclusion?",
        "code": """-- Control region:  n=800, default_rate=18%
-- Pilot region:     n=800, default_rate=14%
-- p-value = 0.03, alpha = 0.05""",
        "opts": [
            "Reject the null hypothesis — the 4% reduction is statistically significant at alpha=0.05. Before full rollout, assess practical significance (cost savings vs implementation cost) and whether the pilot region is representative.",
            "The result is not significant — 4% is a small difference",
            "Accept the null hypothesis — the model makes no difference",
            "p = 0.03 proves the model caused the reduction with certainty",
        ],
        "ans": 0,
        "expl": "p=0.03 < alpha=0.05 so we reject H0 — the reduction is statistically significant. However, we never claim certainty of causation from one test. Practical significance, selection bias in the pilot region, and external confounders must all be assessed before full rollout.",
    },
    {
        "cat": "Statistics", "diff": "hard",
        "q": "The Company's default prediction model has precision = 0.72 and recall = 0.41. A colleague suggests raising the classification threshold to improve precision. What is the trade-off?",
        "code": """-- Current threshold: 0.5
-- Precision: 0.72  (of predicted defaults, 72% are real)
-- Recall:    0.41  (of actual defaults, 41% are caught)
-- Class split: 92% non-default, 8% default""",
        "opts": [
            "Raising the threshold increases precision (fewer false positives) but further decreases recall (more actual defaults are missed). Evaluate using F1-score or a business cost matrix weighting missed defaults vs false alerts.",
            "Raising the threshold always improves both precision and recall",
            "Recall = 0.41 means the model is 41% accurate overall",
            "Precision is always more important than recall for credit models",
        ],
        "ans": 0,
        "expl": "Precision and recall have an inverse trade-off at different thresholds. A higher threshold means the model only flags very confident defaults — fewer false positives (higher precision) but more actual defaults are missed (lower recall). In credit, a missed default is a financial loss. Use F1-score or a cost matrix to find the optimal business threshold.",
    },
    {
        "cat": "Statistics", "diff": "hard",
        "q": "You want to test whether repayment rates differ significantly across The Company's 5 regional branches. Which statistical approach is correct?",
        "code": """-- Branches: Nairobi, Mombasa, Kisumu, Nakuru, Eldoret
-- Metric: repayment_rate per client (continuous, approx. normal)
-- Question: do the means differ across branches?""",
        "opts": [
            "One-way ANOVA to test whether any branch mean differs. If significant (p < alpha), apply Tukey HSD post-hoc test to identify which specific branch pairs differ, controlling family-wise error rate.",
            "Run 10 independent t-tests comparing every branch pair",
            "Chi-squared test on the branch repayment rate counts",
            "Pearson correlation between branch_id and repayment_rate",
        ],
        "ans": 0,
        "expl": "ANOVA tests whether at least one group mean differs across 3+ groups in a single test. Running 10 separate t-tests inflates the Type I error rate — with alpha=0.05 per test, across 10 tests the false positive probability is ~40%. Tukey HSD post-hoc controls this. Branch_id is categorical so correlation is meaningless.",
    },
    {
        "cat": "Statistics", "diff": "medium",
        "q": "In The Company's logistic regression model predicting default, the coefficient for 'loan_term_months' is -0.12. What is the correct interpretation?",
        "code": """-- log-odds(default) = B0 - 0.12*loan_term_months + ...
-- e^(-0.12) ≈ 0.887""",
        "opts": [
            "Each additional month of loan term is associated with an approximately 11.3% decrease in the odds of default (odds ratio = e^-0.12 ≈ 0.887), holding other variables constant.",
            "Each additional month decreases the probability of default by 12%",
            "Longer loans are always safer — this proves causation",
            "The model should remove this variable as the coefficient is negative",
        ],
        "ans": 0,
        "expl": "A negative coefficient means the odds ratio e^-0.12 ≈ 0.887 — each additional month multiplies the odds by 0.887, reducing them by ~11.3%. This is NOT the same as a 12% decrease in probability. Also, this is an association, not causation — longer-term products may simply attract lower-risk clients.",
    },
    {
        "cat": "Scenario", "diff": "hard",
        "q": "The Company's operations team reports the daily disbursement Power BI dashboard shows zero disbursements for yesterday, but the database clearly has records. What are your investigation steps?",
        "code": """-- Dashboard uses DirectQuery to the data warehouse
-- DateTable is a separate imported table
-- Report filter: DateTable[Date] = TODAY()-1""",
        "opts": [
            "1. Check if yesterday's date exists in the DateTable (import may not have refreshed)\n2. Verify the relationship between DateTable and Loans is active and correct\n3. Check DirectQuery connection — confirm warehouse data is accessible\n4. Test the DAX measure in isolation with CALCULATE(..., ALL(DateTable))\n5. Check row-level security — ops team may lack access to recent data",
            "Delete the dashboard and rebuild it from scratch",
            "Change the filter to show all dates and see what appears",
            "The data warehouse must be wrong — escalate to IT immediately",
        ],
        "ans": 0,
        "expl": "Zero results in a DirectQuery dashboard are most commonly caused by: (1) DateTable not refreshed — yesterday's date doesn't exist so the join returns nothing, (2) broken relationship between tables, (3) RLS blocking the user. Systematic diagnosis before escalation prevents unnecessary panic and correctly identifies the root cause.",
    },
    {
        "cat": "Scenario", "diff": "hard",
        "q": "The Company's CFO asks: 'Our average loan size has grown 22% this year, but total disbursements are flat. How is that possible?' How do you explain and investigate this analytically?",
        "code": """-- Year-to-date:
-- Avg loan size: KES 45,000 (was KES 36,900 last year)
-- Total disbursements: ~same as last year""",
        "opts": [
            "If average loan size increases but total disbursements stay flat, the number of loans disbursed must have decreased proportionally. Investigate: (1) loan count by month and branch, (2) whether new client acquisition has slowed, (3) product mix shift toward larger loans for fewer clients, (4) operational capacity constraints.",
            "The financial data must contain errors — recheck all figures",
            "This is impossible — average and total always move together",
            "Total disbursements should be recalculated using median instead",
        ],
        "ans": 0,
        "expl": "Total = Average x Count. If average rises 22% and total is flat, loan count must have fallen by ~18%. The analytical story: The Company may be serving fewer but wealthier clients, or facing acquisition slowdown, or making a strategic shift. Breaking down by branch and product type confirms which.",
    },
    {
        "cat": "Scenario", "diff": "medium",
        "q": "The Company issues bike loans and you are building a Data Quality Checker for the loan application dataset. The 'bike_value_kes' column has suspiciously high values — some entries appear to be in USD instead of KES (1 USD ≈ 130 KES). How do you detect and handle this programmatically?",
        "code": """import pandas as pd
df = pd.read_excel('bike_loans.xlsx')
# bike_value_kes expected range: KES 15,000 - KES 150,000
# USD entries appear as: 500, 800, 1200 (should be 65,000 / 104,000 / 156,000)""",
        "opts": [
            "Q1 = df['bike_value_kes'].quantile(0.25)\nQ3 = df['bike_value_kes'].quantile(0.75)\nIQR = Q3 - Q1\nsuspect_low = df['bike_value_kes'] < Q1 - 1.5 * IQR\ndf.loc[suspect_low, 'bike_value_flag'] = 'Possible USD entry'\ndf.loc[suspect_low, 'bike_value_corrected'] = (\n  df.loc[suspect_low, 'bike_value_kes'] * 130\n)",
            "df = df[df['bike_value_kes'] > 15000]",
            "df['bike_value_kes'] = df['bike_value_kes'] * 130",
            "df.dropna(subset=['bike_value_kes'], inplace=True)",
        ],
        "ans": 0,
        "expl": "USD entries will appear as statistical outliers on the LOW end (e.g. 500 vs expected 65,000+), so we flag values below Q1 - 1.5*IQR. The flag preserves auditability — you cannot be certain every low value is a USD error without manual review. The corrected column multiplies by 130 (USD to KES rate) for review. Option C converts all values indiscriminately, corrupting correctly entered KES values. Option B silently drops data without investigation.",
    },
]

CATEGORIES  = ["All", "SQL", "Python", "Power BI", "Statistics", "Scenario"]
PILL_STYLES = {
    "SQL":        ("🔵", "#E6F1FB", "#0C447C"),
    "Python":     ("🟣", "#EEEDFE", "#3C3489"),
    "Power BI":   ("🟢", "#EAF3DE", "#27500A"),
    "Statistics": ("🟠", "#FAEEDA", "#633806"),
    "Scenario":   ("🔴", "#FAECE7", "#712B13"),
}
DIFF_COLORS = {
    "easy":   ("✅", "#EAF3DE", "#27500A"),
    "medium": ("⚠️", "#FAEEDA", "#633806"),
    "hard":   ("🔴", "#FCEBEB", "#791F1F"),
}
OPTION_LETTERS = ["A", "B", "C", "D"]

# ── Session State ─────────────────────────────────────────────────────────────
def init_state():
    if "answered"       not in st.session_state: st.session_state.answered       = {}
    if "current"        not in st.session_state: st.session_state.current        = 0
    if "cat_filter"     not in st.session_state: st.session_state.cat_filter     = "All"
    if "score"          not in st.session_state: st.session_state.score          = 0
    if "total_answered" not in st.session_state: st.session_state.total_answered = 0

init_state()

def get_filtered():
    f = st.session_state.cat_filter
    return QUESTIONS if f == "All" else [q for q in QUESTIONS if q["cat"] == f]

def clamp_current():
    lst = get_filtered()
    if lst:
        st.session_state.current = max(0, min(len(lst) - 1, st.session_state.current))

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1 style="margin:0;font-size:2rem;">🏦 Senior Data Analytics Practice Quiz</h1>
    <p style="margin:0.5rem 0 0;font-size:1rem;opacity:0.9;">
        Senior Data Analytics · TestDome Preparation · 20 Questions
    </p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🗂️ Filter by Category")
    for cat in CATEGORIES:
        cnt = len(QUESTIONS) if cat == "All" else sum(1 for q in QUESTIONS if q["cat"] == cat)
        label = f"{cat}  ({cnt})"
        active = st.session_state.cat_filter == cat
        btn_type = "primary" if active else "secondary"
        if st.button(label, key=f"cat_{cat}", type=btn_type, use_container_width=True):
            st.session_state.cat_filter = cat
            st.session_state.current    = 0
            st.rerun()

    st.markdown("---")
    correct  = st.session_state.score
    answered = st.session_state.total_answered
    pct      = round(correct / answered * 100) if answered > 0 else 0

    st.markdown(f"""
    <div class="score-card">
        <p style="font-size:0.85rem;color:#555;margin-bottom:4px">Your Score</p>
        <p style="font-size:2rem;font-weight:700;color:#1e3a5f;margin:0">{correct} / {answered}</p>
        <p style="font-size:1rem;color:#2d6a9f;margin:0">{pct}% correct</p>
    </div>
    """, unsafe_allow_html=True)

    st.progress(pct / 100 if answered > 0 else 0)

    if st.button("🔄 Reset Quiz", use_container_width=True, type="secondary"):
        st.session_state.answered       = {}
        st.session_state.current        = 0
        st.session_state.score          = 0
        st.session_state.total_answered = 0
        st.rerun()

    st.markdown("---")
    st.markdown("**Difficulty Legend**")
    st.markdown("🟢 Easy &nbsp;&nbsp; 🟠 Medium &nbsp;&nbsp; 🔴 Hard")

# ── Main Quiz Area ────────────────────────────────────────────────────────────
clamp_current()
filtered = get_filtered()

if not filtered:
    st.info("No questions in this category.")
    st.stop()

total_q    = len(filtered)
cur_idx    = st.session_state.current
q          = filtered[cur_idx]
global_idx = QUESTIONS.index(q)

# Progress bar
st.markdown(f"**Question {cur_idx + 1} of {total_q}**")
st.progress((cur_idx + 1) / total_q)

# Category + difficulty badges
icon, bg, fg               = PILL_STYLES.get(q["cat"], ("", "#eee", "#333"))
diff_icon, diff_bg, diff_fg = DIFF_COLORS.get(q["diff"], ("", "#eee", "#333"))
st.markdown(
    f'<span style="background:{bg};color:{fg};padding:3px 12px;border-radius:8px;'
    f'font-size:0.82rem;font-weight:600;margin-right:8px">{icon} {q["cat"]}</span>'
    f'<span style="background:{diff_bg};color:{diff_fg};padding:3px 10px;border-radius:8px;'
    f'font-size:0.78rem;font-weight:600">{diff_icon} {q["diff"]}</span>',
    unsafe_allow_html=True,
)
st.markdown("<br>", unsafe_allow_html=True)

# Question text
st.markdown(f"### {q['q']}")

# Code block
if q.get("code"):
    st.code(q["code"], language="python" if q["cat"] == "Python" else "sql")

# Answer options
already_answered = global_idx in st.session_state.answered
chosen_answer    = st.session_state.answered.get(global_idx)

st.markdown("**Select your answer:**")

for i, opt in enumerate(q["opts"]):
    letter = OPTION_LETTERS[i]
    if already_answered:
        if i == q["ans"]:
            st.success(f"✅  **{letter}.** Correct answer")
            st.code(opt, language="python" if q["cat"] == "Python" else "sql")
        elif i == chosen_answer and chosen_answer != q["ans"]:
            st.error(f"❌  **{letter}.** Your answer")
            st.code(opt, language="python" if q["cat"] == "Python" else "sql")
        else:
            st.markdown(f"**{letter}.**")
            st.code(opt, language="python" if q["cat"] == "Python" else "sql")
    else:
        # Render full option text as a styled card with a button below
        opt_escaped = opt.replace("\\", "\\\\").replace("`", "\\`")
        lang = "python" if q["cat"] == "Python" else "sql"
        st.markdown(
            f"""
            <div style="
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                padding: 0.6rem 1rem 0.4rem 1rem;
                margin-bottom: 2px;
                background: #fafafa;
                font-family: monospace;
                font-size: 0.85rem;
                white-space: pre-wrap;
                color: #1e1e1e;
                line-height: 1.6;
            "><strong style="font-family:sans-serif;font-size:0.9rem;">{letter}.</strong>  {opt.replace(chr(10), '<br>')}</div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            f"Select {letter}",
            key=f"opt_{global_idx}_{i}",
            use_container_width=True,
        ):
            st.session_state.answered[global_idx] = i
            st.session_state.total_answered += 1
            if i == q["ans"]:
                st.session_state.score += 1
            st.rerun()
        st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)

# Explanation
if already_answered:
    st.markdown(
        f'<div class="expl-box"><strong>Explanation:</strong> {q["expl"]}</div>',
        unsafe_allow_html=True,
    )

# Navigation
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("← Previous", disabled=(cur_idx == 0), use_container_width=True):
        st.session_state.current -= 1
        st.rerun()
with col2:
    answered_count = sum(
        1 for q2 in filtered if QUESTIONS.index(q2) in st.session_state.answered
    )
    st.markdown(
        f"<p style='text-align:center;color:#666;font-size:0.9rem;margin-top:8px'>"
        f"{answered_count} of {total_q} answered in this category</p>",
        unsafe_allow_html=True,
    )
with col3:
    if st.button(
        "Next →",
        disabled=(cur_idx == total_q - 1),
        use_container_width=True,
        type="primary",
    ):
        st.session_state.current += 1
        st.rerun()