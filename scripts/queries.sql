use aurora_dev;

select * from clients;
select * from client_phones;
select * from client_addresses;
select * from phones;
select * from addresses;

select * from countries where id = 36;

delete from addresses where id = 6;

delete from phones where id >= 13;

delete from client_addresses where client_id = 20

INSERT INTO COUNTRIES(name, official_name, alpha_2, alpha_3, numeric_ref, date_create) VALUE('Brazil','Brazil', 'b','BRA',55,CURRENT_DATE)
delete from clients where id = 20;

delete from client_phones where client_id = 20



