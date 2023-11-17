create table client
(
    id          int identity
        primary key,
    name        varchar(100)               not null,
    description varchar(max),
    logo        varchar(250),
    phone       varchar(20),
    created_at  datetime default getdate() not null
)
go

