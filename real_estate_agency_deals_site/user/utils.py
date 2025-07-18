from django.db.models import Count, Q, Subquery, OuterRef
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import IntegerField
from django.contrib.auth import logout
from django.db import IntegrityError
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from user import models
from enum import Enum


def ban_user_action(request, username):
    if request.user.is_anonymous:
        messages.warning(request, 'Авторизуйтесь, чтобы заблокировать пользователя')
        return redirect('login', permanent=False)

    try:
        action_user = models.User.objects.get(username=username)
    except ObjectDoesNotExist:
        messages.error(request, 'Невозможно заблокировать не существующего пользователя')
        return redirect('home', permanent=False)

    if action_user.banned:
        messages.error(request, 'Пользователь уже заблокирован')
        return redirect('user_profile', username=username, permanent=False)

    if action_user.is_staff or action_user.is_superuser:
        messages.error(request, 'Нельзя заблокировать персонал, перед этим нужно удалить права')
        return redirect('user_profile', username=username, permanent=False)

    if not request.user.is_superuser:
        messages.error(request, 'Только администратор может заблокировать пользователя')
        return redirect('user_profile', username=username, permanent=False)

    action_user.banned = True
    action_user.save()

    models.Notification.objects.create(
        to_whom=action_user,
        message='Вы были заблокированы',
        link=reverse('appeal_new'),
    )

    return redirect('user_profile', username=username, permanent=False)


def unban_user_action(request, username):
    if request.user.is_anonymous:
        messages.warning(request, 'Авторизуйтесь, чтобы разблокировать пользователя')
        return redirect('login', permanent=False)

    try:
        action_user = models.User.objects.get(username=username)
    except ObjectDoesNotExist:
        messages.error(request, 'Невозможно разблокировать не существующего пользователя')
        return redirect('home', permanent=False)

    if not action_user.banned:
        messages.error(request, 'Пользователь не заблокирован')
        return redirect('user_profile', username=username, permanent=False)

    if action_user.is_staff or action_user.is_superuser:
        messages.error(request, 'Персонал не может быть заблокирован')
        return redirect('user_profile', username=username, permanent=False)

    if not request.user.is_superuser:
        messages.error(request, 'Только администратор может разблокировать пользователя')
        return redirect('user_profile', username=username, permanent=False)

    action_user.banned = False
    action_user.save()

    models.Notification.objects.create(
        to_whom=action_user,
        message='Вы были разблокированы',
    )

    return redirect('user_profile', username=username, permanent=False)


def give_rights_staff(request, username):
    if request.user.is_anonymous:
        messages.warning(request, 'Авторизуйтесь, чтобы дать права агента недвижимости пользователю')
        return redirect('login', permanent=False)

    try:
        action_user = models.User.objects.get(username=username)
    except ObjectDoesNotExist:
        messages.error(request, 'Невозможно дать права агента недвижимости не существующему пользователя')
        return redirect('home', permanent=False)

    if action_user.is_staff:
        messages.error(request, 'Пользователь уже агент недвижимости')
        return redirect('user_profile', username=username, permanent=False)

    if not request.user.is_superuser:
        messages.error(request, 'Только администратор может дать права агента недвижимости пользователю')
        return redirect('user_profile', username=username, permanent=False)

    action_user.is_staff = True
    action_user.save()

    models.Notification.objects.create(
        to_whom=action_user,
        message='Вам выдали права агента недвижимости',
    )

    return redirect('user_profile', username=username, permanent=False)


def revoke_rights_staff(request, username):
    if request.user.is_anonymous:
        messages.warning(request, 'Авторизуйтесь, чтобы лишить права агента недвижимости пользователя')
        return redirect('login', permanent=False)

    try:
        action_user = models.User.objects.get(username=username)
    except ObjectDoesNotExist:
        messages.error(request, 'Невозможно лишить права агента недвижимости не существующего пользователя')
        return redirect('home', permanent=False)

    if not action_user.is_staff:
        messages.error(request, 'Пользователь не является агентом недвижимости')
        return redirect('user_profile', username=username, permanent=False)

    if not request.user.is_superuser:
        messages.error(request, 'Только администратор может лишить права агента недвижимости пользователю')
        return redirect('user_profile', username=username, permanent=False)

    action_user.is_staff = False
    action_user.save()

    models.Notification.objects.create(
        to_whom=action_user,
        message='Вас лишили прав агента недвижимости',
    )

    return redirect('user_profile', username=username, permanent=False)


class ResultBLAction(Enum):
    SUCCESS = 0
    OTHER_ERROR = 1
    NOT_AUTHORIZED = 2
    USER_NOT_FOUND = 3
    ALREADY_IN_BL = 4
    NO_IN_BL = 5


def bl_add_action(request, username) -> ResultBLAction:
    if request.user.is_anonymous:
        messages.warning(request, 'Авторизуйтесь, чтобы внести в черный список пользователя')
        return ResultBLAction.NOT_AUTHORIZED

    try:
        action_user = models.User.objects.get(username=username)
    except ObjectDoesNotExist:
        messages.error(request, 'Пользователь не найден')
        return ResultBLAction.USER_NOT_FOUND

    if action_user == request.user:
        messages.error(request, 'Вы не можете добавить себя в свой черный список')
        return ResultBLAction.OTHER_ERROR

    try:
        models.BlackList.objects.create(
            whose_BL=request.user,
            who_on_BL=action_user,
        )
    except IntegrityError:
        messages.error(request, 'Пользователя уже находиться в черном списке')
        return ResultBLAction.ALREADY_IN_BL

    return ResultBLAction.SUCCESS

def bl_del_action(request, username) -> ResultBLAction:
    if request.user.is_anonymous:
        messages.warning(request, 'Авторизуйтесь, чтобы вынести из черного списка пользователя')
        return ResultBLAction.NOT_AUTHORIZED

    try:
        action_user = models.User.objects.get(username=username)
    except ObjectDoesNotExist:
        messages.error(request, 'Пользователь не найден')
        return ResultBLAction.USER_NOT_FOUND

    if action_user == request.user:
        messages.error(request, 'Вы не быть в свой черном списоке')
        return ResultBLAction.OTHER_ERROR

    try:
        models.BlackList.objects.get(
            whose_BL=request.user,
            who_on_BL=action_user,
        ).delete()
    except ObjectDoesNotExist:
        messages.error(request, 'Пользователь не находиться в черном списке')
        return ResultBLAction.ALREADY_IN_BL

    return ResultBLAction.SUCCESS


def create_bl_action_router(bl_action, default='home', **routes):
    route_mapping = { member.name: routes.get(member.name) for member in ResultBLAction }

    def router_bl(request, username):
        route = route_mapping.get(bl_action(request, username).name)

        kwargs_redirect = {
            'permanent': False
        }

        if route:
            if route[1]:
                kwargs_redirect['username'] = username
            return redirect(route[0], **kwargs_redirect)

        return redirect(default, **kwargs_redirect)

    return router_bl

routes_profile={
    ResultBLAction.SUCCESS.name: ('user_profile', True,),
    ResultBLAction.OTHER_ERROR.name: ('user_profile', True,),
    ResultBLAction.NOT_AUTHORIZED.name: ('login', False,),
    ResultBLAction.USER_NOT_FOUND.name: ('home', False,),
    ResultBLAction.ALREADY_IN_BL.name: ('user_profile', True,),
    ResultBLAction.NO_IN_BL.name: ('user_profile', True,),
}

routes_my_list={
    ResultBLAction.SUCCESS.name: ('my_black_list', False,),
    ResultBLAction.OTHER_ERROR.name: ('my_black_list', False,),
    ResultBLAction.NOT_AUTHORIZED.name: ('login', False,),
    ResultBLAction.USER_NOT_FOUND.name: ('home', False,),
    ResultBLAction.ALREADY_IN_BL.name: ('my_black_list', False,),
    ResultBLAction.NO_IN_BL.name: ('my_black_list', False,),
}


def get_user_chats(user):
    last_message_subquery = models.PrivateMessage.non_deleted.filter(
        Q(wrote_PM=user, received_PM=OuterRef('pk')) |
        Q(wrote_PM=OuterRef('pk'), received_PM=user)
    ).order_by('-date_write').values('message')[:1]

    last_date_subquery = models.PrivateMessage.non_deleted.filter(
        Q(wrote_PM=user, received_PM=OuterRef('pk')) |
        Q(wrote_PM=OuterRef('pk'), received_PM=user)
    ).order_by('-date_write').values('date_write')[:1]

    other_users = models.User.objects.filter(
        Q(wrote_PM_fk__received_PM=user, wrote_PM_fk__deleted=False) |
        Q(received_PM_fk__wrote_PM=user, received_PM_fk__deleted=False)
    ).distinct()

    unread_count_subquery = models.PrivateMessage.non_deleted.filter(
        wrote_PM=OuterRef('pk'),
        received_PM=user,
        viewed=False,
        deleted=False
    ).order_by().values('wrote_PM').annotate(
        count=Count('*')
    ).values('count')

    other_users = other_users.annotate(
        unread_count=Subquery(unread_count_subquery, output_field=IntegerField()),  # info! можно в целом и без `output_field`
        last_message=Subquery(last_message_subquery),
        last_date=Subquery(last_date_subquery)
    ).order_by('-last_date', '-unread_count')

    chats = []
    for other_user in other_users:
        chats.append({
            'user': {
                'id': other_user.id, # TODO! del см. шаблон в макете или нет
                'username': other_user.username,
                'photo': other_user.photo.url if other_user.photo else None,
            },
            'unread_count': other_user.unread_count,
            'last_message': other_user.last_message,
            'last_date': other_user.last_date
        })

    return chats

def del_private_message(request, pk):
    if request.user.is_anonymous:
        messages.warning(request, 'Авторизуйтесь, чтобы удалить сообщение авторизуйтесь')
        return redirect('home', permanent=False)

    try:
        message: models.PrivateMessage = models.PrivateMessage.non_deleted.get(pk=pk)
    except ObjectDoesNotExist:
        messages.error(request, 'Сообщение не найдено')
        return redirect('home', permanent=False)

    if message.wrote_PM != request.user:
        messages.error(request, 'У вас нет прав на удаление чужого сообщения')
        return redirect('home', permanent=False)

    message.deleted = True
    message.save()
    return redirect('private_message_user', username=message.received_PM.username, permanent=False)

def disable_account_action(request):
    if request.user.is_anonymous:
        messages.warning(request, 'У вас нет учетной записи')
        return redirect('login', permanent=False)

    request.user.is_active = False
    request.user.save()
    return redirect('home', permanent=False)

def logout_action(request):
    if request.user.is_authenticated:
        logout(request)

    return redirect('home', permanent=False)
