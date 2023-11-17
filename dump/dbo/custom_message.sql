create table custom_message
(
    id                 int identity
        primary key,
    custom_question_id int          not null
        constraint custom_message_fk_custom_question
            references custom_question
            on delete cascade,
    user_id            int          not null
        constraint custom_message_fk_user
            references [user]
            on delete cascade,
    message            varchar(max) not null
)
go

