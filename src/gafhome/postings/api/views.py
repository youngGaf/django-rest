from django.db.models import Q
from rest_framework import generics, mixins
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny

from .permissions import IsOwnerOrReadOnly
from postings.models import BlogPost
from .serializers import BlogPostSerializers, RegisterSerializer


class BlogPostAPIView(mixins.CreateModelMixin, generics.ListAPIView):
    lookup_field = 'pk'
    serializer_class = BlogPostSerializers

    def get_queryset(self):
        qs = BlogPost.objects.all()
        query = self.request.GET.get('q')

        if query is not None:
            qs = qs.filter(Q(title__icontains=query)
                           | Q(content__icontains=query)).distinct()
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    # grants access to the request object in serializer
    def get_serializer_context(self, *args, **kwargs):
        return {'request': self.request}


class BlogPostRudView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'pk'
    serializer_class = BlogPostSerializers
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        return BlogPost.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    # def get_object(self):
    #     pk = self.kwargs.get('pk')
    #     return BlogPost.objects.get(pk=pk)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

