from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response


def get_create_delete_related_response(request, create_delete_model,
                                       serializer, response_messages,
                                       **kwargs):
    user = request.user
    instance = list(kwargs.values())[0]
    model_kwargs = {}
    model_kwargs['user'] = user
    model_kwargs.update(kwargs)

    if request.method == 'GET':
        if create_delete_model.objects.filter(**model_kwargs).exists():
            return Response(
                response_messages.get('exists'),
                status=status.HTTP_400_BAD_REQUEST
            )

        create_delete_model.objects.create(**model_kwargs)
        serializer = serializer(instance, context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    elif request.method == 'DELETE':
        create_delete_instance = get_object_or_404(create_delete_model,
                                                   **model_kwargs)
        if not create_delete_instance:
            return Response(
                response_messages.get('not'),
                status=status.HTTP_400_BAD_REQUEST
            )
        create_delete_instance.delete()
        return Response(
            response_messages.get('deleted'),
            status=status.HTTP_204_NO_CONTENT,
        )
