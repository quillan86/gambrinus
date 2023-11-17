create table user_group
(
    user_id  int not null
        references [user]
            on delete cascade,
    group_id int not null
        references [group]
            on delete cascade,
    primary key (user_id, group_id)
)
go

