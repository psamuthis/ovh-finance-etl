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

-- ?
select 
    concat(t.year, '-', t.month) as date
    sp.flavor,
    sum(sp.size) as total_price
from dim_current_savings_plan sp
join dim_time t on t.id = sp.fk_period_from
group by 1, 2, 3
order by 1, 2;


-- over quota per flavor across the year/month
with non_cumulative_over_quota as (
    select t.year as year,
    t.month as month,
    foq.flavor as flavor,
    foq.price - coalesce(
        lag(foq.price) over(
            partition by foq.flavor, date_trunc('month', t.timestamptz)
            order by t.timestamptz
        ),
        0
    ) as daily_non_cumulative_over_quota
    from fact_savings_plan_over_quota foq
    join dim_time t on t.id = foq.fk_created_at
)
select concat(year, '-', month) as date, flavor, sum(daily_non_cumulative_over_quota)
from non_cumulative_over_quota
group by date,flavor, year, month
order by year, month;