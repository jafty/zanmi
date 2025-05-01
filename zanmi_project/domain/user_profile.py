# domain/event.py
from datetime import date, datetime
from domain.user import User

class UserProfile:
    def __init__(
        self,
        user: User,
        avatar: str = "avatars/default.jpg",
        description: str = "",
        birth_date: date = None,
        city: str = "",
        country: str = "",
        languages_spoken: str = "",
        centers_of_interest: str = "",
        event_expectations: str = "",
        activity_preferences: str = "",
        group_size_preference: str = "",
        dietary_restrictions: str = "",
        is_certified: bool = False,
        consent_date: datetime = None,
        slug: str = ""
    ):
        self.user = user
        self.avatar = avatar
        self.description = description
        self.birth_date = birth_date
        self.city = city
        self.country = country
        self.languages_spoken = languages_spoken
        self.centers_of_interest = centers_of_interest
        self.event_expectations = event_expectations
        self.activity_preferences = activity_preferences
        self.group_size_preference = group_size_preference
        self.dietary_restrictions = dietary_restrictions
        self.is_certified = is_certified
        self.consent_date = consent_date
    
    def can_edit(self, user: User) -> bool:
        return self.user.username == user.username

    def get_age(self, current_date: date) -> int | None: # Added Union[int, None] for clarity
        if not self.birth_date:
            return None
        age = current_date.year - self.birth_date.year
        if (current_date.month < self.birth_date.month or
            (current_date.month == self.birth_date.month and current_date.day < self.birth_date.day)):
            age -= 1
        return age
