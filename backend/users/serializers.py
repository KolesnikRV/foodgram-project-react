from rest_framework import serializers

from recipes.models import Subscription

from .models import User


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField('user_is_subscribed')

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def user_is_subscribed(self, user):
        curr_user = self.context.get('request').user
        if curr_user.is_anonymous:
            return False
        return Subscription.objects.filter(user=curr_user,
                                           author=user).exists()
