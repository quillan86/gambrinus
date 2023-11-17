create table [group]
(
    id          int identity
        primary key,
    name        varchar(max) not null,
    description varchar(max) not null
)
go

