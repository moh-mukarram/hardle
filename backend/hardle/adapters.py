from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from .models import UserProfile


class HardleSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom allauth adapter that ensures a UserProfile is created
    for every user who signs in via Google OAuth.
    """

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        # Create UserProfile if it doesn't exist yet (idempotent)
        UserProfile.objects.get_or_create(user=user)
        return user
