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