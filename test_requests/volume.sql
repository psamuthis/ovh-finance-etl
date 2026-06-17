-- total price/usage for each type/region of volume (high-speed, classic, ...)
select t.name as tenant, r.name as region, d.name as deployment_mode, st.type as volume_type, sum(fv.value) as total_usage, u.unit as usage_unit, sum(fv.price) as total_price from fact_current_dynamic_volume fv
join dim_volume v on v.id = fv.fk_volume
join dim_region r on r.id = v.fk_region
join dim_unit u on u.id = fv.fk_unit
join dim_deployment_mode d on d.id = v.fk_deployment_mode
join dim_storage_type st on st.id = v.fk_type join dim_tenant t on t.id = v.fk_tenant
group by t.name, r.name, d.name, st.type, u.unit;

-- usage/price over time of individual volumes
select volume.volume_uuid, "time".timestamptz, fv.price, fv.value as usage, unit.unit from fact_current_dynamic_volume fv
join dim_volume volume on volume.id = fv.fk_volume
join dim_time "time" on "time".id = fv.fk_created_at
join dim_unit unit on unit.id = fv.fk_unit
group by volume.volume_uuid, "time".timestamptz, fv.price, fv.value, unit.unit
order by volume.volume_uuid, "time".timestamptz;