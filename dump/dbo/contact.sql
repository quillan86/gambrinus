create table contact
(
    id         int identity
        primary key,
    name       varchar(200)               not null,
    email      varchar(200)               not null,
    message    nvarchar(max)              not null,
    created_at datetime default getdate() not null
)
go

