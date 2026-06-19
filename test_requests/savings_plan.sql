-- savings plan per flavor per month (check duplicate)
select sp.*, t.timestamptz, t2.timestamptz from dim_current_savings_plan sp
join dim_time t on t.id = sp.fk_period_from
join dim_time t2 on t2.id = sp.fk_period_to
group by sp.id, sp.flavor, t.timestamptz, t2.timestamptz
order by t.timestamptz, t2.timestamptz;

-- env per flavor with associated over_quota
SELECT 
    name,
    flavor,
    size,
    price,
    month,
    NULL AS total_over_quota
FROM (
    SELECT 
        dsp.name,
        dsp.size,
        dsp.flavor,
        dsp.price,
        t.month
    FROM dim_current_savings_plan dsp
    JOIN dim_time t ON t.id = dsp.fk_period_from
    GROUP BY dsp.name, t.month, dsp.size, dsp.flavor, dsp.price
) AS env_data

UNION ALL

SELECT 
    'over_quota' AS name,
    over_quota.flavor AS flavor,
    NULL AS size,
    NULL AS price,
    NULL AS month,
    over_quota.total_over_quota
FROM (
    SELECT oq.flavor as flavor, sum(oq.price) AS total_over_quota
    FROM fact_savings_plan_over_quota oq
    JOIN dim_time t ON t.id = oq.fk_created_at
    group by oq.flavor
) AS over_quota; 