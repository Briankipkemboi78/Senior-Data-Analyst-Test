SELECT 
  client_id,
  SUM(outstanding_balance) AS total_outstanding_balance
FROM loans
WHERE
  status = 'Active'
GROUP BY
  client_id
HAVING COUNT(loan_id) > 1;


---------------------------Missing Payment ----------
SELECT 
  repay.repayment_id,
  sc.client_id,
  sc.loan_id,
  sc.due_date,
  sc.expected_amount,
  repay.amount_paid,
  repay.payment_date
FROM repayments AS repay
LEFT JOIN schedules AS sc ON 
  repay.loan_id = sc.loan_id
  AND DATE_TRUNC('month', r.payment_date) = DATE_TRUNC('month', sc.due_date)
WHERE
  DATE_TRUNC('month', sc.due_date) = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
  AND r.repayment_id IS NULL



  ----------------------------------------------------
 WITH overdue_schedules AS (
    -- Instalments that are more than 30 days past due
    SELECT 
      DISTINCT loan_id
    FROM schedules
    WHERE due_date < CURRENT_DATE - 30
    AND schedule_id NOT IN (
        SELECT schedule_id
        FROM repayments
        WHERE amount_paid >= expected_amount
    )
),

active_loans AS (
    -- Only active loans with their outstanding balances
    SELECT
        loan_id,
        outstanding_balance,
        CASE
            WHEN loan_id IN (SELECT loan_id FROM overdue_schedules)
            THEN outstanding_balance
            ELSE 0
        END AS at_risk_balance
    FROM loans
    WHERE status = 'active'
)

SELECT
    SUM(at_risk_balance)                        AS par30_balance,
    SUM(outstanding_balance)                    AS total_portfolio,
    DIVIDE(
        SUM(at_risk_balance),
        NULLIF(SUM(outstanding_balance), 0)
    )                                           AS par30_rate
FROM active_loans

---------------------------------------------------
SELECT 
  DATE_TRUNC('month', registration_date) AS month,
  COUNT(*)                               AS new_clients,
  SUM(
    COUNT(*)) OVER 
      (ORDER BY DATE_TRUNC('month', registration_date)) AS cumulative_clients
FROM clients 
GROUP BY 1
ORDER BY 1

------------------------------------------------------------
WITH officer_collections AS (
    -- Aggregate total paid and expected per officer per branch
    SELECT
        l.branch_id,
        l.officer_id,
        SUM(r.amount_paid)                          AS total_collected,
        SUM(l.expected_total)                       AS total_expected
    FROM loans l
    LEFT JOIN repayments r ON l.loan_id = r.loan_id
    GROUP BY
        l.branch_id,
        l.officer_id
),

officer_rates AS (
    -- Calculate collection rate and rank within each branch
    SELECT
        branch_id,
        officer_id,
        total_collected,
        total_expected,
        DIVIDE(
            total_collected,
            NULLIF(total_expected, 0)
        )                                           AS collection_rate,
        RANK() OVER (
            PARTITION BY branch_id
            ORDER BY DIVIDE(
                total_collected,
                NULLIF(total_expected, 0)
            ) DESC
        )                                           AS rnk
    FROM officer_collections
)

SELECT
    branch_id,
    officer_id,
    total_collected,
    total_expected,
    collection_rate
FROM officer_rates
WHERE rnk = 1
ORDER BY
    branch_id


  