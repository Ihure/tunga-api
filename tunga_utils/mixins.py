from rest_framework.mixins import CreateModelMixin, UpdateModelMixin

from tunga_utils.models import Upload


class GetCurrentUserAnnotatedSerializerMixin(object):
    """
    Get current user from context
    """

    def get_current_user(self):
        request = self.context.get("request", None)
        if request:
            user = getattr(request, "user", None)
            if user and user.is_authenticated():
                return user
        return None


class SaveUploadsMixin(CreateModelMixin, UpdateModelMixin):

    def perform_create(self, serializer):
        instance = serializer.save()
        self.save_uploads(instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        self.save_uploads(instance)

    def save_uploads(self, content_object):
        uploads = self.request.FILES
        if uploads:
            for uploaded_file in uploads.itervalues():
                upload = Upload(content_object=content_object, file=uploaded_file, user=self.request.user)
                upload.save()
