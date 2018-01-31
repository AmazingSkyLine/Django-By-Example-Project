from rest_framework import serializers
from ..models import Subject, Course, Module, Content

class SubjectSerializer(serializers.ModelSerializer):
    # ModelSerializer 序列化模型实例
    class Meta:
        model = Subject
        fields = ('id', 'title', 'slug')

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ('order', 'title', 'description')

class CourseSerializer(serializers.ModelSerializer):
    # 嵌套序列化对象
    # many 表明序列化多个对象
    # read_only 只读属性
    modules = ModuleSerializer(many=True, read_only=True)
    class Meta:
        model = Course
        fields = ('id', 'subject', 'title', 'slug', 'overview',
                  'created', 'owner', 'modules')

class ItemRelatedField(serializers.ModelSerializer):
    def to_representation(self, instance):
        return instance.render()

class ContentSerializer(serializers.ModelSerializer):
    # 嵌套序列化对象
    item = ItemRelatedField(read_only=True)
    class Meta:
        model = Content
        fields = ('order', 'item')

class ModuleWithContentsSerializer(serializers.ModelSerializer):
    contents = ContentSerializer(many=True)
    class Meta:
        model = Module
        fields = ('order', 'title', 'description', 'contents')

class CourseWithContentSerializer(serializers.ModelSerializer):
    modules = ModuleWithContentsSerializer(many=True)
    class Meta:
        model = Course
        fields = ('id', 'subject', 'title', 'slug',
                  'overview', 'created', 'owner', 'modules')