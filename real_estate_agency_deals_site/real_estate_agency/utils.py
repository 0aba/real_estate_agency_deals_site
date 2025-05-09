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

    messages.success(request, 'Отзыв был успешно удален')

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
    messages.success(request, 'Риэлтор был успешно удален')

    return redirect('realtor_list', permanent=False)

def del_real_estate(request, pk):
    if request.user.is_anonymous:
        messages.warning(request, 'Авторизуйтесь, чтобы удалить недвижимость')
        return redirect('home', permanent=False)

    try:
        real_estate = models.RealEstate.non_deleted.get(pk=pk)
    except ObjectDoesNotExist:
        messages.error(request, 'Недвижимость не найдено')
        return redirect('real_estate_list', permanent=False)

    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав на удаление недвижимости, вы должны быть агент недвижимости')
        return redirect('real_estate_list', permanent=False)

    if models.Deal.non_deleted.filter(
            real_estate_deal=real_estate,
    ).exists():
        messages.error(request, 'Нельзя удалить недвижимость, если с ней связана активная сделка')
        return redirect('real_estate_list', permanent=False)

    real_estate.deleted = True
    real_estate.save()

    messages.success(request, 'Недвижимость была успешно удалена')

    return redirect('real_estate_list', permanent=False)

def del_deal(request, title_slug):
    if request.user.is_anonymous:
        messages.warning(request, 'Авторизуйтесь, чтобы удалить сделку')
        return redirect('login', permanent=False)

    try:
        deal = models.Deal.non_deleted.get(title_slug=title_slug)
    except ObjectDoesNotExist:
        messages.error(request, 'Сделка не найдена')
        return redirect('deal_list', permanent=False)

    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав на удаление сделки, вы должны быть агент недвижимости')
        return redirect('deal_list', permanent=False)

    deal.deleted = True
    deal.save()

    messages.success(request, 'Сделка была успешно удалена')

    return redirect('deal_list', permanent=False)

def reject_deal(request, title_slug):
    if request.user.is_anonymous:
        messages.warning(request, 'Что бы отклонить сделку, нужно авторизоваться')
        return redirect('login', permanent=False)

    if not request.user.is_staff:
        messages.error(request, 'Что бы отклонить сделку, нужно быть агентом недвижимости')
        return redirect('home', permanent=False)

    try:
        current_deal = models.Deal.objects.get(title_slug=title_slug)
    except ObjectDoesNotExist:
        messages.error(request, 'Сделки не существует')
        return redirect('deal_list', permanent=False)

    if current_deal.completed_type != models.Deal.DealCompletedType.IN_PROGRESS:
        messages.error(request, 'Сделка должна быть в статусе "В процессе совершения", чтобы совершить это действие')
        return redirect('deal', title_slug=title_slug, permanent=False)

    current_deal.completed_type = models.Deal.DealCompletedType.REJECTED
    current_deal.save()

    messages.success(request, 'Сделка была отменена успешно')

    return redirect('deal', title_slug=title_slug, permanent=False)

def track_deal(request, title_slug):
    if request.user.is_anonymous:
        messages.warning(request, 'Авторизуйтесь, чтобы следить за сделкой')
        return redirect('login', permanent=False)

    try:
        deal = models.Deal.non_deleted.get(title_slug=title_slug)
    except ObjectDoesNotExist:
        messages.error(request, 'Сделка не найдена')
        return redirect('deal_list', permanent=False)

    if models.TrackDeal.objects.filter(
            track_deal=deal,
            who_track=request.user,
    ).exists():
        messages.error(request, 'Вы уже следите за сделкой')
        return redirect('deal', title_slug=title_slug, permanent=False)

    models.TrackDeal.objects.create(
        track_deal=deal,
        who_track=request.user,
    )

    return redirect('deal', title_slug=title_slug, permanent=False)

def stop_track_deal(request, title_slug):
    if request.user.is_anonymous:
        messages.warning(request, 'Авторизуйтесь, чтобы перестать следить за сделкой')
        return redirect('login', permanent=False)

    try:
        deal = models.Deal.non_deleted.get(title_slug=title_slug)
    except ObjectDoesNotExist:
        messages.error(request, 'Сделка не найдена')
        return redirect('deal_list', permanent=False)

    try:
        models.TrackDeal.objects.get(
            track_deal=deal,
            who_track=request.user,
        ).delete()
    except ObjectDoesNotExist:
        messages.error(request, 'Вы не следите за сделкой')
        return redirect('deal', title_slug=title_slug, permanent=False)

    return redirect('deal', title_slug=title_slug, permanent=False)
