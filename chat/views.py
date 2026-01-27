
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from chat.models import Thread

User = get_user_model()

@login_required
def messages_page(request):
    threads = (
        Thread.objects.by_user(user=request.user)
        .prefetch_related("chatmessage_thread")
        .order_by("timestamp")
    )
    all_workers = User.objects.exclude(id=request.user.id)
    context = {"Threads": threads, "all_workers": all_workers}
    return render(request, "chat/messages.html", context)


@login_required
@require_POST
def start_chat(request):
    other_user_id = request.POST.get("other_user_id")
    if not other_user_id:
        return redirect("chat:messages_page")
    other_user = get_object_or_404(User, id=other_user_id)
    user = request.user
    # Ensure thread uniqueness regardless of order
    thread, created = Thread.objects.get_or_create(
        first_person=min(user, other_user, key=lambda u: u.id),
        second_person=max(user, other_user, key=lambda u: u.id),
    )
    return redirect(f"{reverse('chat:messages_page')}?thread_id={thread.id}")
