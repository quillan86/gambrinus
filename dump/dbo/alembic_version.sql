create table alembic_version
(
    version_num varchar(32) not null
        constraint alembic_version_pkc
            primary key
)
go

