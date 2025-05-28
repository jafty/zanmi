from domain.user_profile import UserProfile
from domain.user import User
from domain.repositories.user_profile_repository import UserProfileRepository
from .models import UserProfileDB
from django.contrib.auth import get_user_model
from django.conf import settings


class DjangoUserProfileRepository(UserProfileRepository):
    def get_by_user_id(self, user_id: int) -> UserProfile:
        print("USE ID")
        print(user_id)
        db_users = get_user_model()
        user_to_match = db_users.objects.get(id=user_id)
        db_profile, _ = UserProfileDB.objects.get_or_create(user=user_to_match)
        # domain user might also need a separate fetch
        domain_user = User(username=db_profile.user.username)
        # build the domain object
        return UserProfile(
            user=domain_user,
            avatar=db_profile.avatar if db_profile.avatar else f"{settings.MEDIA_URL}avatars/default.jpg",
            description=db_profile.description or "",
            birth_date=db_profile.birth_date,
            city=db_profile.city,
            country=db_profile.country,
            languages_spoken=db_profile.languages_spoken or "",
            centers_of_interest=db_profile.centers_of_interest or "",
            event_expectations=db_profile.event_expectations or "",
            perfect_outing_description=db_profile.perfect_outing_description or "",
            music_preference=db_profile.music_preference or "",
            fun_fact=db_profile.fun_fact or "",
            group_size_preference=db_profile.group_size_preference or "",
            dietary_restrictions=db_profile.dietary_restrictions or "",
            is_certified=db_profile.is_certified,
            consent_date=db_profile.consent_date,
        )

    def save_user_profile(self, profile: UserProfile) -> None:
        UserDB = get_user_model()
        django_user = UserDB.objects.get(username=profile.user.username)
        try:
            db_profile = UserProfileDB.objects.get(user=django_user)
        except UserProfileDB.DoesNotExist:
            db_profile = UserProfileDB(user=django_user)
        db_profile.avatar = profile.avatar
        db_profile.description = profile.description
        db_profile.birth_date = profile.birth_date
        db_profile.city = profile.city
        db_profile.country = profile.country
        db_profile.languages_spoken = profile.languages_spoken
        db_profile.centers_of_interest = profile.centers_of_interest
        db_profile.event_expectations = profile.event_expectations
        db_profile.perfect_outing_description = profile.perfect_outing_description
        db_profile.music_preference = profile.music_preference
        db_profile.fun_fact = profile.fun_fact
        db_profile.group_size_preference = profile.group_size_preference
        db_profile.dietary_restrictions = profile.dietary_restrictions
        db_profile.is_certified = profile.is_certified
        db_profile.consent_date = profile.consent_date
        print("PROFILE AVATAR DB BEFORE SAVE")
        print(db_profile.avatar)
        db_profile.save()
        print("PROFILE AVATAR DB AFTER SAVE:")
        print(db_profile.avatar)