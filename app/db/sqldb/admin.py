from sqladmin import ModelView
from .schema import Client, User, Session, Response, Address, Contact, Cookie, Group, Permission, CustomQuestion, CustomMessage


class ClientAdmin(ModelView, model=Client):
    name = "Client"
    name_plural = "Clients"
    icon = "fa-solid fa-briefcase"
    page_size = 25
    page_size_options = [25, 50, 100, 200]
    column_list = [Client.id, Client.name, Client.logo, Client.phone, Client.description]
    column_formatters = {Client.description: lambda m, a: m.description[:50]}
    column_searchable_list = [Client.name]
    column_sortable_list = [Client.id]


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    page_size = 25
    page_size_options = [25, 50, 100, 200]
    column_list = [User.id, User.email, User.first_name, User.last_name, User.photo, User.title, User.client]
    column_searchable_list = [User.email, User.first_name, User.last_name]
    column_sortable_list = [User.id]


class AddressAdmin(ModelView, model=Address):
    name = "Address"
    name_plural = "Addresses"
    icon = "fa-solid fa-address-book"
    page_size = 25
    page_size_options = [25, 50, 100, 200]
    column_list = [Address.id, Address.client, Address.street, Address.city, Address.state, Address.zip_code, Address.country]
    column_searchable_list = [Address.street, Address.city, Address.zip_code, Address.country]
    column_sortable_list = [Address.id]


class SessionAdmin(ModelView, model=Session):
    name = "Session"
    name_plural = "Sessions"
    icon = "fa-solid fa-bars"
    page_size = 25
    page_size_options = [25, 50, 100, 200]
    column_list = [Session.id, Session.user, Session.name, Session.created_at]
    column_searchable_list = [Session.name]
    column_sortable_list = [Session.id]


class ResponseAdmin(ModelView, model=Response):
    name = "Response"
    name_plural = "Responses"
    icon = "fa-solid fa-reply"
    page_size = 25
    page_size_options = [25, 50, 100, 200]
    column_list = [Response.id, Response.session, Response.human_created_at, Response.feedback_check, Response.feedback_category, Response.question, Response.answer]
    column_formatters = {Response.question: lambda m, a: m.question[:75], Response.answer: lambda m, a: m.answer[:75]}
    column_searchable_list = [Response.question, Response.answer]
    column_sortable_list = [Response.id]


class CustomQuestionAdmin(ModelView, model=CustomQuestion):
    name = "Custom Question"
    name_plural = "Custom Questions"
    icon = "fa-solid fa-question"
    page_size = 25
    page_size_options = [25, 50, 100, 200]
    column_list = [CustomQuestion.id, CustomQuestion.question, CustomQuestion.prompt]
    column_formatters = {CustomQuestion.question: lambda m, a: m.question[:75], CustomQuestion.prompt: lambda m, a: m.prompt[:75]}
    column_searchable_list = [CustomQuestion.question]
    column_sortable_list = [CustomQuestion.id]


class CustomMessageAdmin(ModelView, model=CustomMessage):
    name = "Custom Message"
    name_plural = "Custom Messages"
    icon = "fa-solid fa-message"
    page_size = 25
    page_size_options = [25, 50, 100, 200]
    column_list = [CustomMessage.id, CustomMessage.custom_question, CustomMessage.user, CustomMessage.message]
    column_formatters = {CustomMessage.message: lambda m, a: m.message[:100]}
    column_searchable_list = [CustomMessage.message]
    column_sortable_list = [CustomMessage.id]


class ContactAdmin(ModelView, model=Contact):
    name = "Contact"
    name_plural = "Contacts"
    icon = "fa-sharp fa-solid fa-address-card"
    page_size = 25
    page_size_options = [25, 50, 100, 200]
    column_list = [Contact.id, Contact.name, Contact.email, Contact.message, Contact.created_at]
    column_searchable_list = [Contact.name, Contact.email, Contact.message]
    column_sortable_list = [Contact.id]


class CookieAdmin(ModelView, model=Cookie):
    name = "Cookie"
    name_plural = "Cookies"
    icon = "fa-solid fa-cookie"
    page_size = 25
    page_size_options = [25, 50, 100, 200]
    column_list = [Cookie.id, Cookie.user, Cookie.token, Cookie.created_at, Cookie.updated_at, Cookie.expires_at]
    column_searchable_list = [Cookie.token]
    column_sortable_list = [Cookie.id]


class PermissionAdmin(ModelView, model=Permission):
    name = "Permission"
    name_plural = "Permissions"
    icon = "fa-solid fa-ruler-vertical"
    can_create = False
    can_delete = False
    page_size = 25
    page_size_options = [25, 50, 100, 200]
    column_list = [Permission.id, Permission.name, Permission.description]
    column_searchable_list = [Permission.name]
    column_sortable_list = [Permission.id]


class GroupAdmin(ModelView, model=Group):
    name = "Group"
    name_plural = "Groups"
    icon = "fa-solid fa-user-group"
    can_create = False
    can_delete = False
    page_size = 25
    page_size_options = [25, 50, 100, 200]
    column_list = [Group.id, Group.name, Group.description]
    column_searchable_list = [Group.name]
    column_sortable_list = [Group.id]


admin_views = {
    'client': ClientAdmin,
    'address': AddressAdmin,
    'user': UserAdmin,
    'session': SessionAdmin,
    'response': ResponseAdmin,
    'custom_question': CustomQuestionAdmin,
    'custom_message': CustomMessageAdmin,
    'permission': PermissionAdmin,
    'group': GroupAdmin,
    'cookie': CookieAdmin,
    'contact': ContactAdmin
}
