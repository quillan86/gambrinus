create table cookie
(
    id         int identity
        primary key,
    user_id    int         not null
        references [user]
            on delete cascade,
    token      varchar(50) not null,
    created_at datetime    not null,
    updated_at datetime    not null,
    expires_at datetime    not null
)
go

