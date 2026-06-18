-- all storage names when they have some price or value that is not 0
select s.name from dim_storage s
join fact_current_dynamic_storage fs on fs.fk_storage = s.id
where (fs.in_bandwidth_value > 0 or fs.in_bandwidth_price > 0
or fs.out_bandwidth_value > 0 or fs.out_bandwidth_price > 0) and s.name != '';

select fs.in_bandwidth_value, fs.in_bandwidth_price,
    fs.out_bandwidth_value, fs.out_bandwidth_price,
    fs.in_internal_bandwidth_value, fs.in_internal_bandwidth_price,
    fs.out_internal_bandwidth_value, fs.out_internal_bandwidth_price,
    fs.retrieval_fees_value, fs.retrieval_fees_price,
    fs.stored_value, fs.stored_price
    from fact_current_dynamic_storage fs
join dim_storage s on s.id = fs.fk_storage
where s.name = 'asp-ia-prod';