from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sessions.models import Session
from django.contrib.auth import logout
from django.db import IntegrityError
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
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

    if action_user.is_staff:
        messages.error(request, 'Нельзя заблокировать администрацию')
        return redirect('user_profile', username=username, permanent=False)

    if not request.user.is_staff:
        messages.error(request, 'Только администратор может заблокировать пользователя')
        return redirect('user_profile', username=username, permanent=False)

    action_user.banned = True
    action_user.is_online = False
    action_user.save()

    sessions = Session.objects.filter(expire_date__gte=timezone.now())

    for session in sessions:
        data = session.get_decoded()
        if data.get('_auth_user_id') == str(action_user.id):
            session.delete()


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

    if action_user.is_staff:
        messages.error(request, 'Администрация не может быть заблокирован')
        return redirect('user_profile', username=username, permanent=False)

    if not request.user.is_staff:
        messages.error(request, 'Только администратор может разблокировать пользователя')
        return redirect('user_profile', username=username, permanent=False)

    action_user.banned = False
    action_user.save()

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
    ResultBLAction.SUCCESS.name: ('my_black_list', True,),
    ResultBLAction.OTHER_ERROR.name: ('my_black_list', True,),
    ResultBLAction.NOT_AUTHORIZED.name: ('login', False,),
    ResultBLAction.USER_NOT_FOUND.name: ('home', False,),
    ResultBLAction.ALREADY_IN_BL.name: ('my_black_list', True,),
    ResultBLAction.NO_IN_BL.name: ('my_black_list', True,),
}

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
