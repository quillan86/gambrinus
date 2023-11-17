create table [user]
(
    id         int identity
        primary key,
    email      varchar(100)               not null
        constraint UQ__user__B4EC43D4B4DB951B
            unique,
    first_name varchar(100),
    last_name  varchar(100),
    photo      varchar(250),
    title      varchar(100),
    client_id  int
        constraint user_fk_client
            references client
            on delete cascade,
    created_at datetime default getdate() not null
)
go

