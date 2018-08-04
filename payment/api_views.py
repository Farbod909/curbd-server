from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions

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
        )

    except:
        return Response(status=402)
    else:
        return Response(status=200)