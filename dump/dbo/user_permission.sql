create table user_permission
(
    user_id       int not null
        references [user],
    permission_id int not null
        references permission,
    primary key (user_id, permission_id)
)
go

