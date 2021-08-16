from django.contrib.auth import login
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.generic import UpdateView, ListView, CreateView
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.urls import reverse, reverse_lazy

from django.contrib import messages

from .models import Blogger, Reader

from .forms import BoardForm, NewTopicForm, PostForm, BloggerSignUpForm, ReaderSignUpForm
from .models import Board, Post, Topic


class BoardListView(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'home.html'
    paginate_by = 5


class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
        return queryset


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'topic_posts.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        session_key = 'viewed_topic_{}'.format(self.topic.pk)
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True
        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset


@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user
            topic.save()
            Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=request.user
            )
            return redirect('topic_posts', pk=pk, topic_pk=topic.pk)
    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})


@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.last_updated = timezone.now()
            topic.save()

            topic_url = reverse('topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk})
            topic_post_url = '{url}?page={page}#{id}'.format(
                url=topic_url,
                id=post.pk,
                page=topic.get_page_count()
            )

            return redirect(topic_post_url)
    else:
        form = PostForm()
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message',)
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)


class BloggerSignUpView(CreateView):
    model = Blogger
    form_class = BloggerSignUpForm
    template_name = 'signup_form.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'blogger'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_blogger = True
        login(self.request, user)
        return redirect('home')


class ReaderSignUpView(CreateView):
    model = Reader
    form_class = ReaderSignUpForm
    template_name = 'signup_form.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'reader'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')


def save_board_form(request, form, template_name, data):
    data = data
    print(request)


    page = request.GET.get('page', 1)

    if request.method == 'POST':

        if form.is_valid():
            form.save()

            data['form_is_valid'] = True
            boards = Board.objects.all()

            paginator = Paginator(boards, 5)
            try:
                board = paginator.page(page)
            except PageNotAnInteger:
                board = paginator.page(1)
            except EmptyPage:
                board = paginator.page(paginator.num_pages)

            data['html_home'] = render_to_string('partials/partial_board_list.html', {
                'boards': board
            })


        else:
            data['form_is_valid'] = False
    context = {'form': form, 'page_num': page}

    data['html_form'] = render_to_string(template_name, context, request=request)
    # my_message = messages.success(request, 'Board updated!', extra_tags=None)
    # data['html_messages'] = render_to_string('partials/messages.html', context={'my_message': my_message} ,request=request)

    return JsonResponse(data)


def board_create(request):
    data = dict()
    if request.method == 'POST':
        form = BoardForm(request.POST)
    else:
        form = BoardForm()
    my_message = messages.success(request, 'Board has been created!', extra_tags=None)
    data['html_messages'] = render_to_string('partials/messages.html', context={'message': my_message},
                                             request=request)
    return save_board_form(request, form, 'partials/partial_board_create.html', data)


def board_update(request, pk):
    data = dict()
    board = get_object_or_404(Board, pk=pk)

    if request.method == 'POST':
        form = BoardForm(request.POST, instance=board)

    else:
        form = BoardForm(instance=board)
    my_message = messages.success(request, 'Board "{}" has been updated!'.format(board.name), extra_tags=None)
    data['html_messages'] = render_to_string('partials/messages.html', context={'message': my_message},
                                             request=request)

    return save_board_form(request, form, 'partials/partial_board_update.html', data)


def board_delete(request, pk):
    board = get_object_or_404(Board, pk=pk)
    data = dict()
    if request.method == 'POST':
        board.delete()
        data['form_is_valid'] = True  # This is just to play along with the existing code
        boards = Board.objects.all()
        data['html_home'] = render_to_string('partials/partial_board_list.html', {
            'boards': boards
        })
    else:
        context = {'board': board}
        data['html_form'] = render_to_string('partials/partial_board_delete.html',
                                             context,
                                             request=request,
                                             )
    my_message = messages.success(request, 'Board "{}" has been deleted!'.format(board.name), extra_tags=None)
    data['html_messages'] = render_to_string('partials/messages.html', context={'message': my_message},
                                             request=request)
    return JsonResponse(data)
