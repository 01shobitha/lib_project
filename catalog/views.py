import datetime
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from catalog.models import Book, Author, BookInstance, Genre
from django.views import generic
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from catalog.forms import RenewBookForm, TimeForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from catalog.models import Author
from django.utils import timezone

# Create your views here.

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_genres = Genre.objects.all().count()


    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()
    time =timezone.now()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres':num_genres,
        'num_visits': num_visits,
        'time': time,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    context_object_name = 'book_list'
    queryset = Book.objects.all()
    template_name = 'catalog/book_list.html'
    paginate_by = 10

class BookDetailView(generic.DetailView):
    model = Book
    def book_detail_view(request, primary_key):
        book = get_object_or_404(Book, pk=primary_key)
        return render(request, 'catalog/book_detail.html', context={'book': book})

class AuthorListView(generic.ListView):
    model = Author
    context_object_name = 'author_list'
    queryset = Author.objects.all()
    template_name='catalog/author_list.html'

class AuthorDetailView(generic.DetailView):
    model = Author
    def author_detail_view(request, primary_key):
        author=get_object_or_404(Author)
        return render(request, 'catalog/author_detail.html', context={'author' : author})

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

#challenge
class BorrewedBooksListView(PermissionRequiredMixin, generic.ListView):
    model=BookInstance
    permission_required='catalog.can_mark_returned'
    template_name='catalog/bookinstance_list_borrowed_all.html'
    paginate_by=10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        book_renewal_form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if book_renewal_form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = book_renewal_form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        book_renewal_form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': book_renewal_form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018'}

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')

class BookCreate(CreateView):
    model = Book
    fields = '__all__'

class BookUpdate(UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']

class BookDelete(DeleteView):
    model=Book
    success_url=reverse_lazy('books')

# def request_page(request):
#     time = timezone.now()
#     book=Book(Changetime)
#     if(request.method=='GET'):
#         if(book.Changetime==True):
#             time = datetime.strftime(time,"%H:%M")
#             book.Changetime=False
#         else:
#             time = datetime.strftime(time, "%I:%M %p")
#             book.Changetime=True
#         context = {
#         'time': time,
#         }
#     return render(request, 'request_page.html', context)

def time_view(request):
    form = TimeForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            display_type = request.POST.get("display_type", None)
            # if display_type in ["12_hours", "24_hours"]:
            if display_type =="12_hours":
                Changetime=True
            else:
                Changetime=False
    context = {
        'Changetime': Changetime,
    }
    return render(request, 'index.html', {'form': form}, context=context)
