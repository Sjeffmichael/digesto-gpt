from .models import Conversation


def conversations_list(request):
    if request.user.is_authenticated:
        return {
            "conversations": Conversation.objects.filter(
                user_id=request.user.id
            ).order_by("-created_date")
        }
    return {}
