from rest_framework import generics
from ..models import Subject, Course
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from .permissions import IsEnrolled
from .serializer import CourseWithContentSerializer, CourseSerializer

'''
class SubjectListView(generics.ListAPIView):
    # 检索所有Subject
    # queryset：基础查询集用来取回对象
    queryset = Subject.objects.all()
    # 序列化使用的类
    # serializer_class：这个类用来序列化对象
    serializer_class = SubjectSerializer

class SubjectDetailView(generics.RetrieveAPIView):
    # 期待一个主键参数(pk)，如id
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

# 参与课程的API
class CourseEnrollView(APIView):
    # 认证使用的类
    authentication_classes = (BasicAuthentication, )
    # 限制权限访问
    permission_classes = (IsAuthenticated, )
    # post期待一个课程id
    def post(self, request, pk, format=None):
        course = get_object_or_404(Course, pk=pk)
        course.students.add(request.user)
        return Response({'enroll': True})
'''

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    # 继承ReadOnlyModelViewSet类的子类，
    # 被继承的类提供了只读的操作 list()和retrieve()
    # 前者用来排列对象(list)，后者用来取回一个单独的对象(detail)
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    # 给视图添加一个额外的enroll操作
    @detail_route(methods=['post'],
                  authentication_classes=[BasicAuthentication],
                  permission_classes=[IsAuthenticated])
    def enroll(self, request, *args, **kwargs):
        # 期待一个主键参数(pk)
        # 获取课程对象
        course = self.get_object()
        course.students.add(request.user)
        return Response({'enroll': True})

    @detail_route(methods=['get'],
                  serializer_class=CourseWithContentSerializer,
                  authentication_classes=[BasicAuthentication],
                  permission_classes=[IsAuthenticated,IsEnrolled])
    # 只有在这个课程中报名的用户才能访问这个课程的内容
    # 方法名即是路由
    def contents(self, request, *args, **kwargs):
        # retrieve()获取一个课程对象
        return self.retrieve(request, *args, **kwargs)