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

    return redirect('deal_list', permanent=False)

def completed_deal(request, title_slug):
    if request.user.is_anonymous:
        messages.warning(request, 'Авторизуйтесь, чтобы завершить сделку')
        return redirect('login', permanent=False)

    try:
        deal = models.Deal.non_deleted.get(title_slug=title_slug)
    except ObjectDoesNotExist:
        messages.error(request, 'Сделка не найдена')
        return redirect('deal_list', permanent=False)

    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав на завершение сделки, вы должны быть агент недвижимости')
        return redirect('deal', title_slug=title_slug, permanent=False)

    if deal.completed:
        messages.error(request, 'Сделка уже завершена')
        return redirect('deal', title_slug=title_slug, permanent=False)

    deal.completed = True
    deal.save()

    return redirect('deal', title_slug=title_slug, permanent=False)


def make_rented_deal(request, title_slug):
    if request.user.is_anonymous:
        messages.warning(request, 'Авторизуйтесь, чтобы пометить сделку как арендуемую')
        return redirect('login', permanent=False)

    try:
        deal = models.Deal.non_deleted.get(
            title_slug=title_slug,
            type=models.Deal.DealType.RENT,
        )
    except ObjectDoesNotExist:
        messages.error(request, 'Сделка аренды не найдена')
        return redirect('deal_list', permanent=False)

    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав на то, чтобы пометить сделку арендуемой, вы должны быть агент недвижимости')
        return redirect('deal', title_slug=title_slug, permanent=False)

    if deal.completed:
        messages.error(request, 'Сделка завершена')
        return redirect('deal', title_slug=title_slug, permanent=False)

    data_rental = models.DataRental.objects.get(deal_rental=deal)

    if data_rental.rented:
        messages.error(request, 'Сделка уже является арендуемой')
        return redirect('deal', title_slug=title_slug, permanent=False)

    data_rental.rented = True
    data_rental.save()

    return redirect('deal', title_slug=title_slug, permanent=False)

def make_unrented_deal(request, title_slug):
    if request.user.is_anonymous:
        messages.warning(request, 'Авторизуйтесь, чтобы пометить сделку как не арендуемую')
        return redirect('login', permanent=False)

    try:
        deal = models.Deal.non_deleted.get(
            title_slug=title_slug,
            type=models.Deal.DealType.RENT,
        )
    except ObjectDoesNotExist:
        messages.error(request, 'Сделка аренды не найдена')
        return redirect('deal_list', permanent=False)

    if not request.user.is_staff:
        messages.error(request,
                       'У вас нет прав на то, чтобы пометить сделку не арендуемой, вы должны быть агент недвижимости')
        return redirect('deal', title_slug=title_slug, permanent=False)

    if deal.completed:
        messages.error(request, 'Сделка завершена')
        return redirect('deal', title_slug=title_slug, permanent=False)

    data_rental = models.DataRental.objects.get(deal_rental=deal)

    if not data_rental.rented:
        messages.error(request, 'Сделка уже является арендуемой')
        return redirect('deal', title_slug=title_slug, permanent=False)

    data_rental.rented = False
    data_rental.save()

    return redirect('deal', title_slug=title_slug, permanent=False)

