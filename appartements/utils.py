from .models import JournalActivite

def enregistrer_activite(
    request,
    module,
    action,
    description
):

    JournalActivite.objects.create(

        utilisateur=request.user,

        module=module,

        action=action,

        description=description

    )