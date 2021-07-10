from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.views import LoginView, PasswordChangeView, LogoutView
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Sum
from django.urls import reverse_lazy
from core.utils import get_client_ip
from posts.models import Comment, Post
from .forms import (
    LoginForm,
    PostForm,
    PostFilterForm,
    CommentForm,
    CommentFilterForm,
    ProfileForm,
    ChangePasswordForm
)


class RegisterUser(LoginView):
    template_name = 'users/d.html'
    form_class = LoginForm
    success_url = '/profile/'
    redirect_authenticated_user = True


class LoginUser(LoginView):
    template_name = 'users/d.html'
    form_class = LoginForm
    success_url = '/profile/'
    redirect_authenticated_user = True


class UserDashboard(LoginRequiredMixin, TemplateView):
    template_name = 'users/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        temp_posts = Post.objects.filter(is_published=True)
        user_posts = temp_posts.filter(author=self.request.user)
        comments = Comment.objects.filter(is_approved=True, post__author=self.request.user)
        context['total_posts_count'] = user_posts.count()
        context['total_views_count'] = user_posts.aggregate(Sum('views'))['views__sum']
        context['total_comments_count'] = comments.count()
        context['rank'] = int((context['total_views_count'] * 100) / temp_posts.aggregate(Sum('views'))['views__sum'])
        context['post_list'] = user_posts.order_by('-views')[:10]
        context['current_page'] = 'dashboard'
        return context


class AllPosts(LoginRequiredMixin, ListView):
    template_name = 'users/all-posts.html'
    paginate_by = 20

    def get_queryset(self):
        posts = Post.objects.filter(author=self.request.user).order_by('-modified_date')
        category = self.request.GET.get('category')
        if category:
            posts = posts.filter(categories__id=category)
        tag = self.request.GET.get('tag')
        if tag:
            posts = posts.filter(tags__id=tag)
        term = self.request.GET.get('term')
        if term:
            posts = posts.filter(title__icontains=term)
        status = self.request.GET.get('status')
        if status == 'published':
            posts = posts.filter(is_published=True)
        elif status == 'draft':
            posts = posts.filter(is_published=False)
        return posts
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'posts'
        context['current_sub_page'] = 'all_posts'
        context['search_form'] = PostFilterForm(self.request.GET or None)
        b_url = '?'
        category = self.request.GET.get('category')
        if category:
            b_url += f'category={category}&'
        tag = self.request.GET.get('tag')
        if tag:
            b_url += f'tag={tag}&'
        term = self.request.GET.get('term')
        if term:
            b_url += f'term={term}&'
        status = self.request.GET.get('status')
        if status:
            b_url += f'status={status}&'
        context['base_url'] = b_url
        return context


class NewPost(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    form_class = PostForm
    template_name = 'users/user-form.html'
    success_url = reverse_lazy('user_all_posts')
    success_message = "'%(title)s' was created successfully."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'posts'
        context['current_sub_page'] = 'new_post'
        return context
    
    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.action_ip = get_client_ip(self.request)
        return super().form_valid(form)


class EditPost(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = PostForm
    template_name = 'users/user-form.html'
    success_url = reverse_lazy('user_all_posts')
    success_message = "'%(title)s' was edited successfully."

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'posts'
        context['current_sub_page'] = 'all_posts'
        return context


class DeletePost(LoginRequiredMixin, DeleteView):
    template_name = 'users/user-form.html'
    success_url = reverse_lazy('user_all_posts')
    context_object_name = 'del_post'

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'posts'
        context['current_sub_page'] = 'all_posts'
        return context


class AllComments(LoginRequiredMixin, ListView):
    template_name = 'users/all-comments.html'
    paginate_by = 20

    def get_queryset(self):
        comments = Comment.objects.filter(post__author=self.request.user).order_by('-created_date')
        term = self.request.GET.get('term')
        if term:
            comments = comments.filter(body__icontains=term)
        status = self.request.GET.get('status')
        if status == 'approved':
            comments = comments.filter(is_approved=True)
        elif status == 'pending':
            comments = comments.filter(is_approved=False)
        return comments
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'comments'
        context['search_form'] = CommentFilterForm(self.request.GET or None)
        b_url = '?'
        term = self.request.GET.get('term')
        if term:
            b_url += f'term={term}&'
        status = self.request.GET.get('status')
        if status:
            b_url += f'status={status}&'
        context['base_url'] = b_url
        return context


class EditComment(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = CommentForm
    template_name = 'users/user-form.html'
    success_url = reverse_lazy('user_all_comments')
    success_message = "Comment status changed successfully."

    def get_queryset(self):
        return Comment.objects.filter(post__author=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'comments'
        return context


class DeleteComment(LoginRequiredMixin, DeleteView):
    template_name = 'users/user-form.html'
    success_url = reverse_lazy('user_all_comments')
    context_object_name = 'del_comment'

    def get_queryset(self):
        return Comment.objects.filter(post__author=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'comments'
        return context


class UserProfile(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = 'users/profile.html'
    form_class = ProfileForm
    success_url = reverse_lazy('user_edit_profile')
    success_message = 'Profile updated successfully'

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return User.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'profile'
        return context


class DeleteUser(LoginRequiredMixin, DeleteView):
    template_name = 'users/user-form.html'
    success_url = '/' # reverse_lazy('homepage')
    context_object_name = 'del_user'

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return User.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'profile'
        return context


class ChangePassword(LoginRequiredMixin, PasswordChangeView):
    template_name = 'users/user-form.html'
    form_class = ChangePasswordForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'password'
        context['password'] = True
        return context


class LogoutUser(LoginRequiredMixin, LogoutView):
    pass