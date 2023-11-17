create table group_permission
(
    group_id      int not null
        references [group]
            on delete cascade,
    permission_id int not null
        references permission
            on delete cascade,
    primary key (group_id, permission_id)
)
go

