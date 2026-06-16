select k.flavor, sum(dc.usage_price) as total_price, sum(dc.usage_value) as total_runtime from fact_current_dynamic_compute dc
join dim_kubernetes k on k.id = dc.fk_resource
join dim_unit u on u.id = dc.fk_usage_unit
group by k.flavor
order by total_price;