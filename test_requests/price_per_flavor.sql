select t.name, k.flavor, sum(dc.usage_price) as total_price, sum(dc.usage_value) as total_runtime from fact_current_dynamic_compute dc
join dim_kubernetes k on k.id = dc.fk_resource
join dim_tenant t on k.fk_tenant = t.id
join dim_unit u on u.id = dc.fk_usage_unit
group by t.name, k.flavor
order by total_price;