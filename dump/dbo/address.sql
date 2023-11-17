create table address
(
    id        int identity
        primary key,
    client_id int not null
        constraint address_fk_client
            references client,
    street    varchar(250),
    city      varchar(100),
    state     varchar(100),
    zip_code  varchar(20),
    country   varchar(100),
    latitude  numeric(9, 6),
    longitude numeric(9, 6)
)
go

