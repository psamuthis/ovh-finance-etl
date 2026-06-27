-- total price/usage for each type/region of volume (high-speed, classic, ...)
select 
    concat(t.year, '-', t.month) as "date",
    st.type as volume_type, 
    sum(fv.price) as total_price 
from fact_current_dynamic_volume fv
join dim_volume v on v.id = fv.fk_volume
join dim_storage_type st on st.id = v.fk_type
join dim_time t on t.id = fv.fk_period_from
group by t.year, t.month, st.type 
order by t.year, t.month, volume_type;

-- usage/price over time of individual volumes
select volume.volume_uuid, "time".timestamptz, fv.price, fv.value as usage, unit.unit from fact_current_dynamic_volume fv
join dim_volume volume on volume.id = fv.fk_volume
join dim_time "time" on "time".id = fv.fk_created_at
join dim_unit unit on unit.id = fv.fk_unit
group by volume.volume_uuid, "time".timestamptz, fv.price, fv.value, unit.unit
order by volume.volume_uuid, "time".timestamptz;

-- total price of current month
select
    concat(t.year, '-', t.month) as "date"
    sum(fv.price) as total_price
