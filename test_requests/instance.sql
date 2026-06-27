-- total cost and usage of dynamic instances per flavor
select t.name, k.flavor, sum(dc.usage_price) as total_price, sum(dc.usage_value) as total_runtime, u.unit as usage_unit from fact_current_dynamic_compute dc
join dim_kubernetes k on k.id = dc.fk_resource
join dim_tenant t on k.fk_tenant = t.id
join dim_unit u on u.id = dc.fk_usage_unit
group by t.name, k.flavor, u.unit
order by total_price desc;

-- fixed instances total for June
select tenant.name as tenant, kube.flavor as flavor, sum(fc.price) as total_price from fact_current_fixed_compute fc
join dim_kubernetes kube on kube.id = fc.fk_resource
join dim_tenant tenant on tenant.id = kube.fk_tenant
join dim_time "time" on "time".id = fc.fk_created_at
where "time".month = 6
group by tenant.name, kube.flavor
order by total_price desc;


-- non cumulative cost
SELECT
    fdc.instance_id as id,
    DATE(t.timestamptz) as day,
    fdc.usage_price as cumulative_cost,
    fdc.usage_price - COALESCE(
        LAG(fdc.usage_price) OVER (
            PARTITION BY fdc.instance_id 
            ORDER BY DATE(t.timestamptz)
        ),
        0
    ) as daily_non_cumulative_cost
FROM fact_current_dynamic_compute fdc
JOIN dim_time t ON t.id = fdc.fk_created_at
ORDER BY fdc.instance_id, DATE(t.timestamptz);

-- [DYNAMIC] non cumulative cost of flavors per (year,month) 
with non_cumulative_cost as (
    select
        t.year as year,
        t.month as month,
        k.flavor as flavor,
        fdc.usage_price - coalesce(
            lag(fdc.usage_price) over(
                partition by fdc.instance_id, date_trunc('month', t.timestamptz)
                order by t.timestamptz
            ),
            0
        ) as daily_non_cumulative_cost
    from fact_current_dynamic_compute fdc
    join dim_time t on t.id = fdc.fk_created_at
    join dim_kubernetes k on k.id = fdc.fk_resource
)
select concat(year, '-', month) as date, flavor, sum(daily_non_cumulative_cost) 
from non_cumulative_cost
group by 1, 2
order by 1;

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
group by 1, 2
order by 1;

-- [DYNAMIC] non cumulative cost of flavors for the current month
with non_cumulative_cost as (
    select
        t.year as year,
        t.month as month,
        k.flavor as flavor,
        fdc.usage_price - coalesce(
            lag(fdc.usage_price) over(
                partition by fdc.instance_id, date_trunc('month', t.timestamptz)
                order by t.timestamptz
            ),
            0
        ) as daily_non_cumulative_cost
    from fact_current_dynamic_compute fdc
    join dim_time t on t.id = fdc.fk_created_at
    join dim_kubernetes k on k.id = fdc.fk_resource
    where date_trunc('month', t.timestamptz) = date_trunc('month', current_date)
)
select flavor, sum(daily_non_cumulative_cost) as total_cost
from non_cumulative_cost
group by flavor
order by total_cost desc;

-- [FIXED] cost per flavor per month
select 
    to_char(date_trunc('month', t.timestamptz), 'YYYY-MM') as month,
    k.flavor as flavor,
    sum(fdc.price) as total_cost
from fact_current_fixed_compute fdc
join dim_time t on t.id = fdc.fk_created_at
join dim_kubernetes k on k.id = fdc.fk_resource
group by date_trunc('month', t.timestamptz), k.flavor
order by date_trunc('month', t.timestamptz), total_cost desc;

-- [FIXED] cost per flavor for the current month
select 
    date_trunc('month', t.timestamptz) as month,
    k.flavor as flavor,
    sum(fdc.price) as total_cost
from fact_current_fixed_compute fdc
join dim_time t on t.id = fdc.fk_created_at
join dim_kubernetes k on k.id = fdc.fk_resource
where date_trunc('month', t.timestamptz) = date_trunc('month', current_date)
group by date_trunc('month', t.timestamptz), k.flavor
order by total_cost desc;