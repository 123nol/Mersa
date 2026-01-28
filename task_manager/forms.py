from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from task_manager.models import Worker, Task, Workspace, WorkspaceMembership

from task_manager.models import Attachment


class WorkerCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Worker
        fields = ("username", "email", "role")



class TaskForm(forms.ModelForm):
    assignees = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    deadline = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "placeholder": "MM/DD/YYYY", "class": "form-control"}),
        input_formats=["%m/%d/%Y", "%Y-%m-%d"],
        help_text="Format: MM/DD/YYYY",
    )

    def __init__(self, *args, **kwargs):
        # accept `user` kwarg to scope workspace choices
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields["is_completed"].widget.attrs["disabled"] = True
        if 'workspace' in self.fields:
            if user is not None:
                # allow only workspaces where user is at least MEMBER
                allowed_roles = ['ADMIN', 'MANAGER', 'MEMBER']
                self.fields['workspace'].queryset = Workspace.objects.filter(memberships__user=user, memberships__role__in=allowed_roles).distinct()
            else:
                # default to no choices if no user provided
                self.fields['workspace'].queryset = Workspace.objects.none()

    class Meta:
        model = Task
        fields = "__all__"


# Form for uploading attachments
class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ["file"]


class RegistrationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control form-control-lg", "placeholder": "Password"}
        ),
    )
    password2 = forms.CharField(
        label="Password Confirmation",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Password Confirmation",
            }
        ),
    )

    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
        )

        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "Username",
                }
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control form-control-lg", "placeholder": "Email"}
            ),
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "First name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "Last name",
                }
            ),
        }


class TaskSearchForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by task name"}),
    )


class WorkerSearchForm(forms.Form):
    username = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by username"}),
    )
