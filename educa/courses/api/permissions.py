from rest_framework.permissions import BasePermission

# 定制权限，学生对其参与了的课程才有权限
class IsEnrolled(BasePermission):
    def has_object_permission(self, request, view, obj):
        # 判断当前课程中是否有当前用户
        return obj.students.filter(id=request.user.id).exists()