import imp
from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from django.http import HttpResponse
from taggit.models import Tag
from django.db.models import Count


# Create your views here.
def post_list(request,tag_slug=None):
    objects_list = Post.objects.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(objects_list, 1)
    page = request.GET.get('page','')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request,'blog/post/list.html',{
        
        'page' : page,
        'posts': posts,
        'tag' : tag
        })


def post_detail(request,year,month,day,post):
    post = get_object_or_404(Post, slug=post,
                                   status= 'published',
                                   publish__year = year,
                                   publish__month = month,
                                   publish__day = day    
    )

    # list of active comments for this post
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()


    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.objects.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags')[:2]


    return render(request,'blog/post/detail.html',{'post':post,
                                                    'comments': comments,
                                                    'new_comment': new_comment,
                                                    'comment_form': comment_form,
                                                    'similar_posts': similar_posts
                                                    })



def post_share(request, post_id):
    post = get_object_or_404(Post,id=post_id)
    sent = False
    if request.method == 'POST':
    
        form = EmailPostForm(request.POST)
       
        if form.is_valid():
            # return HttpResponse("works")
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n {cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'shaunhossain655@gmail.com',[cd['to']])
            sent = True
    else:
        form = EmailPostForm()
            # return HttpResponse("works else")
    return render(request,'blog/post/share.html',{'post':post,
                                                        'form': form,
                                                        'sent': sent
        })

 
