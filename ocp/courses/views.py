from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, Course, Enrollment, Announcement, Lesson, Material, Teacher
from .forms import ContactCourseForm, CommentForm
from .decorators import enrollment_required
from django.utils.translation import ugettext as _
from .forms import CategoryForm, CourseForm
from django.http import HttpResponseRedirect
from django.views.generic import (TemplateView, View, ListView, DetailView)
# from django.views.decorators.http import last_modified
# from django.views.i18n import javascript_catalog

from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
import datetime


def incharge(request, slug):
    try:
        teacher_id = int(request.POST["teacher"])
        teacher = Teacher.objects.get(pk=teacher_id)
        course = get_object_or_404(Course, slug=slug)
    except KeyError:
        messages.info(request, _("No selection."))
        #return render(request, "error.html", {"message": "No selection."})
    except Course.DoesNotExist:
        messages.info(request, _("No course."))
        #return render(request, "error.html", {"message": "No course."})
    except Course.DoesNotExist:
        messages.info(request, _("No teacher."))
        #return render(request, "error.html", {"message": "No teacher."})
    teacher.course.add(course)
    return HttpResponseRedirect(reverse('courses:course_details', args=(slug,)))

# Faz a inscrição no curso referente ao usuário da sessão.
@login_required
def enrollment(request, slug):
    course = get_object_or_404(Course, slug=slug)
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user, course=course
    )
    if created:
        # enrollment.active()
        messages.success(request, _('You was enrolled in course with success'))
    else:
        messages.info(request, _('You have been enrolled in course'))
    return redirect('accounts:dashboard')

# Cancela a inscrição no curso referente ao usuário da sessão.
@login_required
def enrollment_undo(request, slug):
    course = get_object_or_404(Course, slug=slug)
    enrollment = get_object_or_404(
        Enrollment, user=request.user, course=course
    )
    if request.method == 'POST':
        enrollment.delete()
        messages.success(request, _('Your subscription was successfully canceled'))
        return redirect('accounts:dashboard')
    template = 'courses/enrollment_undo.html'
    context = {
        'enrollment': enrollment,
        'course': course,
    }
    return render(request, template, context)


@login_required
@enrollment_required
def announcements(request, slug):
    course = request.course
    template = 'courses/announcements.html'
    context = {
        'course': course,
        'announcements': course.announcements.all()
    }
    return render(request, template, context)


@login_required
@enrollment_required
def announcement_detail(request, slug, pk):
    course = request.course
    announcement = get_object_or_404(course.announcements.all(), pk=pk)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        # vamos colocar commit=False pois ainda temos que preencher
        # outros valores do objeto comment antes de salvar.
        comment = form.save(commit=False)
        comment.user = request.user
        comment.announcement = announcement
        comment.save()
        form = CommentForm()
        messages.success(request, _('Your comment was sended with success'))
    template = 'courses/announcement_detail.html'
    context = {
        'course': course,
        'announcement': announcement,
        'form': form,
    }
    return render(request, template, context)


@login_required
@enrollment_required
def lesson_list(request, slug):
    course = request.course
    template = 'courses/lesson_list.html'
    lessons = course.release_lessons()
    if request.user.is_staff:
        lessons = course.lessons.all()
    context = {
        'course': course,
        'lessons': lessons
    }
    return render(request, template, context)


@login_required
@enrollment_required
def lesson_detail(request, slug, pk):
    course = request.course
    lesson = get_object_or_404(Lesson, pk=pk, course=course)
    # Incluimos o if abaixo para garantir que o usuario não tentara manipular a URL
    # buscando acessar um curso que ainda não esta disponível para aquela data.
    if not request.user.is_staff and not lesson.is_available():
        messages.error(request, _('This class is not available'))
        return redirect('courses:lesson_list', slug=course.slug)
    template = 'courses/lesson_detail.html'
    context = {
        'course': course,
        'lesson': lesson, }
    return render(request, template, context)

@login_required
@enrollment_required
def material_detail(request, slug, pk):
    course = request.course
    material = get_object_or_404(Material, pk=pk, lesson__course=course)
    lesson = material.lesson

    # Incluimos o if abaixo para garantir que o usuario não tentara manipular a URL
    # buscando acessar um curso que ainda não esta disponível para aquela data.
    if not request.user.is_staff and not lesson.is_available():
        messages.error(request, _('This material is not available.'))
        return redirect('courses:lesson_detail', slug=course.slug, pk=lesson.pk)

    if not material.is_embedded():
         return redirect(material.file.url)
    else:
        file_name = material.file
        video_url = settings.MEDIA_URL + str(file_name)
        context = {
                'course': course,
                'lesson': lesson,
                'material': material,
                'video_show': video_url,
            }
        return render(request, 'courses/show_embedded.html', context)


def video_show(request, image=None):
    if image is None:
        #messages.info(request, _("No Video"))
        #return HttpResponseRedirect(reverse('courses:material_detail', args=(slug,)))
        return render(request, "error.html", {"message": _('No Video.')})

    try:
        video_object = get_object_or_404(material_detail, pk=image)
    except material_detail.DoesNotExist:
        return render(request, "error.html", {"message": _('Id doesnt exists.')})

    file_name = video_object.file
    video_url = settings.MEDIA_URL + file_name
    return render(request, "courses/video_template.html", {"video_show": video_url})


def category_list(request):
    context = {}
    categories = Category.objects.order_by('name')
    if not categories:
        # messages.info(request, _('No category at moment'))
        categories = {}
        courses_category = {}
    else:
        context['category'] = categories[0]
        context['cats'] = categories
        courses_category = Course.objects.filter(category=categories[0])
        if not courses_category:
            # messages.info(request, _('No curse at moment'))
            context['courses_category'] = {}
        else:
            context['courses_category'] = courses_category
    return render(request, 'courses/category_list.html', context)


def category_details(request, pkSlug):
    # Create a context dictionary which we can pass to the template rendering engine.
    context = {}

    categories = Category.objects.order_by('name')
    context = {'cats': categories}

    try:
        category = Category.objects.get(slug=pkSlug)
        context['category_name'] = category.name
        courses_category = Course.objects.filter(category=category)
        if not courses_category:
            context['courses_category'] = {}
        else:
            context['courses_category'] = courses_category
        context['category'] = category
    except Category.DoesNotExist:
        category = None
        context['category'] = category

    return render(request, 'courses/category_list.html', context)


def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)
            return redirect(reverse('courses:category_list'))
        else:
            # The supplied form contained errors - just print them to the terminal.
            print(form.errors)
    else:
        # If the request was not a POST, display the form to enter details.
        form = CategoryForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render(request, 'courses/category_add.html', {'form': form})

def course_add(request, pkSlug):
    try:
        category = Category.objects.get(slug=pkSlug)
    except Category.DoesNotExist:
        messages.info(request, _('That category not exist'))
        category = None

    if request.method == 'POST':
        # //Importante: Para imagem sempre incluir no POST => request.FILES
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.category = category
            course.views = 0
            course.save()
            messages.info(request, _('Course created with success'))
            return redirect(reverse('courses:category_list'))
        else:
            print(form.errors)
    else:
        form = CourseForm()

    context = {'form': form, 'category': category}

    return render(request, 'courses/course_add.html', context)


# Carrega o template com uma lista com todos os cursos no botão do menu "Course"
def course_list(request):
    courses = Course.objects.all()
    template_name = 'courses/index.html'
    context = {
        'courses': courses
    }
    return render(request, template_name, context)


# Este template mostra os "detalhes do curso" e no final da pagina tem um "fale conosco"
def course_details(request, pkSlug):

    course = get_object_or_404(Course, slug=pkSlug)

    #Soma um a views baseado na sessão
    if request.session.get(course.slug, False) == False:
        course.views = course.views + 1
        course.save()
        request.session[course.slug] = str(datetime.date.today())

    context = {}
    if request.method == 'POST':
        form = ContactCourseForm(request.POST)
        if form.is_valid():
            context['is_valid'] = True
            form.send_mail(course)
            form = ContactCourseForm()
    else:
        form = ContactCourseForm()
    context['form'] = form
    context['course'] = course
    context['teachers'] = course.teachers.all()
    context['non_teachers'] = Teacher.objects.exclude(course=course).all()
    template_name = 'courses/course_details.html'
    return render(request, template_name, context)


# A ListView nos fornece a variavel object_list para ser
# recuperada no html
class CourseFilter(ListView):
    template_name = 'courses/index.html'

    def get_queryset(self):
        queryset = Course.objects.all()
        # /Importante: Quando usamos self.request.GET.get('order', '')
        # com GET.Get nos passamos no parametro um string vazio,
        # que será o default para o get se não retornar nada da consulta.
        # o que não ocorre se fizemos apenas: order = self.request.GET('order')
        order = self.request.GET.get('order', '')
        if order == 'created_at':
            queryset = queryset.order_by('-created_at')
        elif order == 'views':
            queryset = queryset.order_by('-views')
        elif order == 'qualification':
            queryset = queryset.order_by('-qualification')
        # /Importante: Como esta view é acessada por duas URLs diferentes
        # a view deve identificar qual URL a acessou para tomar a acão respectiva
        # no caso uma URL encaminha parametros nomeados(Kwargs) e a outra não (Args)
        # abaixo verificamos se a Kwargs tem o nome "tag" se existir é porque foi a
        # URL refente a ordenação de tags.
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CourseFilter, self).get_context_data(**kwargs)
        return context

index = CourseFilter.as_view()