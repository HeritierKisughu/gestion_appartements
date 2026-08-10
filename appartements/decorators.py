from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def role_requis(*roles):

    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if request.user.is_superuser:
                return view_func(
                    request,
                    *args,
                    **kwargs
                )

            groupes = request.user.groups.values_list(
                'name',
                flat=True
            )

            if any(role in groupes for role in roles):

                return view_func(
                    request,
                    *args,
                    **kwargs
                )

            messages.error(
                request,
                "Vous n'avez pas l'autorisation d'accéder à cette page."
            )

            return redirect('dashboard')

        return wrapper

    return decorator