from django.core.mail import send_mail
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from django.urls import reverse


@receiver(reset_password_token_created)
def handle_reset_password_token_created(sender, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    """

    reset_password_url = "{}?token={}".format(reverse('forget-password:reset-password-confirm'), reset_password_token.key)

    send_mail(
        "Curbd Password Reset",
        "Here is your verification link: {}".format(reset_password_url),
        "no-reply@curbdparking.com",
        [reset_password_token.user.email])