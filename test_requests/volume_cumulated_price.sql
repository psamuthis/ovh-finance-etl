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