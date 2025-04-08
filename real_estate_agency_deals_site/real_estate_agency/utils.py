from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from real_estate_agency import models
from django.contrib import messages


def del_review_agency(request, pk):
    if request.user.is_anonymous:
        messages.warning(request, 'Авторизуйтесь, чтобы удалить отзыв об агентстве')
        return redirect('home', permanent=False)

    try:
        review = models.ReviewAgency.non_deleted.get(pk=pk)
    except ObjectDoesNotExist:
        messages.error(request, 'Отвыв об агентстве не найдено')
        return redirect('home', permanent=False)

    if review.wrote_review != request.user:
        messages.error(request, 'У вас нет прав на удаление отзыва об агентстве')
        return redirect('agency_profile', slug_name=review.review_agency.slug_name, permanent=False)

    review.deleted = True
    review.save()
    return redirect('home', permanent=False)


def del_realtor(request, pk):
    if request.user.is_anonymous:
        messages.warning(request, 'Авторизуйтесь, чтобы удалить риэлтора')
        return redirect('home', permanent=False)

    try:
        realtor = models.Realtor.objects.get(pk=pk)
    except ObjectDoesNotExist:
        messages.error(request, 'Риэлтор не найдено')
        return redirect('home', permanent=False)

    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав на удаление риелтора, вы должны быть агент недвижимости')
        return redirect('realtor_list', permanent=False)

    realtor.delete()

    return redirect('realtor_list', permanent=False)
