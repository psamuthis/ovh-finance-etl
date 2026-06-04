select v.volume_uuid, t.timestamptz, fv.price from fact_current_dynamic_volume as fv
join dim_time t on t.id = fv.fk_created_at
join dim_volume v on v.id = fv.fk_volume
group by v.volume_uuid, t.timestamptz, fv.price
order by v.volume_uuid, t.timestamptz;

select v.volume_uuid, t.timestamptz, fv.value from fact_current_dynamic_volume as fv
join dim_time t on t.id = fv.fk_created_at
join dim_volume v on v.id = fv.fk_volume
group by v.volume_uuid, t.timestamptz, fv.value
order by v.volume_uuid, t.timestamptz;

select v.volume_uuid, t.timestamptz, fv.price, fv.value from fact_current_dynamic_volume as fv
join dim_time t on t.id = fv.fk_created_at
join dim_volume v on v.id = fv.fk_volume
group by v.volume_uuid, t.timestamptz, fv.price, fv.value
order by v.volume_uuid, t.timestamptz;

select v.volume_uuid, max(t.timestamptz) as ajd_mai, sum(fv.price) as total_price, sum(fv.value) as total_storage, u.unit, te.name as tenant from fact_current_dynamic_volume as fv
join dim_time t on t.id = fv.fk_created_at
join dim_volume v on v.id = fv.fk_volume
join dim_tenant te on te.id = v.fk_tenant
join dim_unit u on u.id = fv.fk_unit
where t.month = 5
group by tenant, v.volume_uuid, t.timestamptz, u.unit
order by te.name, t.timestamptz, total_price;