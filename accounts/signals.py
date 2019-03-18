from django.core.mail import send_mail
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created, post_password_reset


@receiver(reset_password_token_created)
def handle_reset_password_token_created(sender, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    """

    reset_password_url = "{}?token={}".format('/forget_password/confirm', reset_password_token.key)

    send_mail(
        "Curbd Password Reset Link",
        "Please click the following link on your mobile device to reset your password:\n\n"
        "https://www.curbdparking.com{}\n\n"
        "If you did not request a password reset, please ignore this email.".format(reset_password_url),
        "no-reply@curbdparking.com",
        [reset_password_token.user.email])


@receiver(post_password_reset)
def handle_post_password_reset(sender, user, *args, **kwargs):
    """
    Handles informing user that password was reset
    An e-mail needs to be sent to the user
    """

    send_mail(
        "Curbd Password Reset Successful",
        "Your password was reset successfully. If this was not you please contact support@curbdparking.com immediately.",
        "no-reply@curbdparking.com",
        [user.email])
