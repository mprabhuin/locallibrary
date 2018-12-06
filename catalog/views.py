from django.shortcuts import render
from django.views import generic
from django.contrib.auth.decorators import login_required # this is for general views which are not class based
from django.contrib.auth.mixins import LoginRequiredMixin # this is for class based views
from django.contrib.auth.mixins import PermissionRequiredMixin  # this is for defineing permission in class based views
from django.contrib.auth.decorators import permission_required # this is for  defineing permission in general views which are not class based

# Create your views here.
from catalog.models import Book, Author, BookInstance, Genre, Language

# @login_required
def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    
    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    
    # The 'all()' is implied by default.    
    num_authors = Author.objects.count()
    num_genres = Genre.objects.count()
    num_books_withwind = Book.objects.filter(title__exact='The Name of the Wind').count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1


    
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'num_books_withwind': num_books_withwind,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


# class BookListView(LoginRequiredMixin, generic.ListView):
class BookListView(generic.ListView):
    model = Book
    paginate_by = 10


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    model = Author

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class LoanedBooksByUserAdminListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""

    permission_required = 'catalog.can_mark_returned'
    # Or multiple permissions
    # permission_required = ('catalog.can_mark_returned', 'catalog.can_edit')
    # Note that 'catalog.can_edit' is just an example
    # the catalog application doesn't have such permission!

    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user_admin.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

    
 # sample code for creating forms for book renewal
 #==================================================================================================================
import datetime

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

# importing the renewbook forms from catalog/forms.py
from catalog.forms import RenewBookForm

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

# Code for editing the forms
#==========================================================================================================
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from catalog.models import Author
from catalog.models import Book

class AuthorCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'can_mark_returned'
    model = Author
    fields = '__all__'
    # initial = {'date_of_death': '05/01/2018'}

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'can_mark_returned'
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'can_mark_returned'
    model = Author
    success_url = reverse_lazy('authors') 
    # redirect location by explicitly declaring parameter success_url, we use the reverse_lazy() function to redirect to our author list after an author has been deleted — reverse_lazy() is a lazily executed version of reverse(), used here because we're providing a URL to a class-based view attribute.


class BookCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'can_mark_returned'
    model = Book
    fields = '__all__'
    initial = {'language': '1'}

class BookUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'can_mark_returned'
    model = Book
    fields = ['title', 'author', 'summary', 'isbn','genre', 'language']

class BookDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'can_mark_returned'
    model = Book
    success_url = reverse_lazy('books') 