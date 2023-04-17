from django.http import HttpResponseRedirect
from django.urls import reverse
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    pass

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin): 
        # print(request.user)
        if request.user.is_authenticated:
            sociallogin.connect(request, request.user)
        return

    def is_auto_signup_allowed(self, request, sociallogin):
        return True

    def save_user(self, request, sociallogin, form=None):
        if request.user.is_authenticated:
            sociallogin.connect(request, request.user)
            return request.user

        return super().save_user(request, sociallogin, form)
