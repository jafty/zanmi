from events_app.repositories import DjangoNotificationRepository

def unread_notifications(request):
    if request.user.is_authenticated:
        repo = DjangoNotificationRepository()
        count = repo.count_unread_notifications(request.user.id)
        print(count)
        return {"unread_notifications_count": count}
    return {}

