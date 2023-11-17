create table response
(
    id                   int identity
        primary key,
    session_id           int                        not null
        references session
            on delete cascade,
    assistant_created_at datetime                   not null,
    assistant_updated_at datetime                   not null,
    question             nvarchar(max)              not null,
    answer               nvarchar(max)              not null,
    intent               varchar(50)                not null,
    feedback_check       bit,
    feedback_category    varchar(50),
    feedback_comment     nvarchar(max),
    sources              varchar(max),
    human_created_at     datetime default getdate() not null,
    human_updated_at     datetime default getdate() not null
)
go

