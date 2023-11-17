create table session
(
    id         int identity
        primary key,
    user_id    int          not null
        references [user]
            on delete cascade,
    created_at datetime     not null,
    updated_at datetime     not null,
    name       varchar(max) not null
)
go

create fulltext index []
    on session (name)
	key index PK__session__3213E83F6B179185
go

