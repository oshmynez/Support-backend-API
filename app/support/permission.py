from rest_framework.permissions import IsAdminUser as BaseIsAdminUser


class IsAdminUser(BaseIsAdminUser):
    def has_permission(self, request, view):
        return request.user.is_superuser


