create table custom_question
(
    id       int identity
        primary key,
    question varchar(max) not null,
    prompt   varchar(max) not null
)
go

