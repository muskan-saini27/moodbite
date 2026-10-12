from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm


class RegisterForm(forms.ModelForm):

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "autocomplete": "username",
            }
        ),
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email address",
                "autocomplete": "email",
            }
        ),
    )

    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "autocomplete": "new-password",
            }
        ),
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm password",
                "autocomplete": "new-password",
            }
        ),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
        ]

    def clean_username(self):

        username = self.cleaned_data["username"].strip()

        if User.objects.filter(
            username__iexact=username
        ).exists():

            raise forms.ValidationError(
                "This username is already taken."
            )

        return username

    def clean_email(self):

        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(
            email__iexact=email
        ).exists():

            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email

    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if (
            password
            and confirm_password
            and password != confirm_password
        ):

            raise forms.ValidationError(
                "Passwords do not match."
            )

        return cleaned_data

    def save(self, commit=True):

        user = super().save(commit=False)

        user.username = self.cleaned_data["username"]
        user.email = self.cleaned_data["email"]

        user.set_password(
            self.cleaned_data["password"]
        )

        if commit:
            user.save()

        return user


class LoginForm(AuthenticationForm):

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "autocomplete": "username",
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "autocomplete": "current-password",
            }
        )
    )