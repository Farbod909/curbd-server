from django.core.mail import send_mail
from django.db.models.query import Q

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions

from decouple import config

import datetime
import pytz

from accounts.api_permissions import IsHost
from parking.models import Reservation

import stripe
stripe.api_key = "sk_test_4QCFRtdqrQLuKnFizELDk4i6"


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def ephemeral_keys(request):
    api_version = request.POST['api_version']
    customer_id = request.user.customer.stripe_customer_id

    key = stripe.EphemeralKey.create(customer=customer_id, stripe_version=api_version)
    return Response(key)


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def charge(request):
    amount = request.POST['amount']
    source = request.POST['source']
    # metadata = request.POST['metadata']
    statement_descriptor = request.POST['statement_descriptor']
    customer = request.user.customer.stripe_customer_id

    try:
        stripe.Charge.create(
            amount=amount,
            currency="usd",
            source=source,
            customer=customer,
            description="Charge for " + request.user.email,
            statement_descriptor=statement_descriptor,
            # metadata=metadata
            # TODO: set reservation id as metadata
        )

    except:
        return Response(status=402)
    else:
        return Response(status=200)


@api_view(['POST'])
@permission_classes((IsHost,))
def venmo_payout(request):
    host = request.user.host
    amount = host.available_balance
    venmo_email = request.data.get('venmo_email', host.venmo_email)

    if host.venmo_email != venmo_email:
        host.venmo_email = venmo_email
        host.save()

    Reservation.objects.filter(
        Q(fixed_availability__parking_space__host=host) |
        Q(repeating_availability__parking_space__host=host)).filter(
        paid_out=False).filter(
        end_datetime__lt=datetime.datetime.now(pytz.utc)).filter(
        cancelled=False).update(paid_out=True)

    send_mail(
        '[PAYOUT]',
        "amount: %s,\n venmo email: %s,\n user id: %s,\n user full name: %s" %
        (amount, venmo_email, request.user.id, request.user.get_full_name()),
        'no-reply@curbdparking.com', [config('PAYOUT_REQUEST_RECIPIENT')])

    return Response("Success", 200)
