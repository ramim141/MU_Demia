from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, HttpResponseForbidden
from django.db.models import Q
from .models import Note, Subject, Comment
from django.core.paginator import Paginator

def note_list(request):
    subject = request.GET.get('subject')
    search = request.GET.get('search')
    subjects = Subject.objects.all()
    
    notes = Note.objects.all()
    
    if subject:
        notes = notes.filter(subject__slug=subject)
    
    if search:
        notes = notes.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(subject__name__icontains=search)
        )
    
    paginator = Paginator(notes, 5)  # Show 12 notes per page
    page_number = request.GET.get('page')
    notes = paginator.get_page(page_number)
    
    return render(request, 'notes/note_list.html', {
        'notes': notes,
        'subjects': subjects,
        'current_subject': subject,
        'search_query': search
    })

@login_required
def note_upload(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        subject_id = request.POST.get('subject')
        file = request.FILES.get('file')
        
        if title and description and subject_id and file:
            subject = get_object_or_404(Subject, id=subject_id)
            note = Note.objects.create(
                title=title,
                description=description,
                subject=subject,
                file=file,
                author=request.user
            )
            messages.success(request, 'Note uploaded successfully!')
            return redirect('notes:note_detail', pk=note.pk)
        else:
            messages.error(request, 'Please fill all required fields.')
    
    subjects = Subject.objects.all()
    return render(request, 'notes/note_upload.html', {'subjects': subjects})

def note_detail(request, pk):
    note = get_object_or_404(Note, pk=pk)
    note.increment_view_count()
    
    if request.method == 'POST' and request.user.is_authenticated:
        content = request.POST.get('content')
        rating = request.POST.get('rating')
        if content and rating:
            try:
                rating = int(rating)
                if 1 <= rating <= 5:
                    Comment.objects.create(
                        note=note,
                        author=request.user,
                        content=content,
                        rating=rating
                    )
                    messages.success(request, 'Comment added successfully!')
                else:
                    messages.error(request, 'Rating must be between 1 and 5.')
            except ValueError:
                messages.error(request, 'Invalid rating value.')
            return redirect('notes:note_detail', pk=pk)
    
    comments = note.comments.all()
    return render(request, 'notes/note_detail.html', {
        'note': note,
        'comments': comments
    })

@login_required
def note_download(request, pk):
    note = get_object_or_404(Note, pk=pk)
    # Increment download count
    note.download_count += 1
    note.save()
    
    # Return the file for download
    response = FileResponse(note.file.open('rb'))
    response['Content-Disposition'] = f'attachment; filename="{note.file.name}"'
    return response

@login_required
def edit_note(request, pk):
    note = get_object_or_404(Note, pk=pk)
    
    # Check if user is the author
    if note.author != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to edit this note.")
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        subject_id = request.POST.get('subject')
        file = request.FILES.get('file')
        
        if title and description and subject_id:
            subject = get_object_or_404(Subject, id=subject_id)
            note.title = title
            note.description = description
            note.subject = subject
            if file:
                note.file = file
            note.save()
            messages.success(request, 'Note updated successfully!')
            return redirect('notes:note_detail', pk=note.pk)
        else:
            messages.error(request, 'Please fill all required fields.')
    
    subjects = Subject.objects.all()
    return render(request, 'notes/note_edit.html', {
        'note': note,
        'subjects': subjects
    })

@login_required
def delete_note(request, pk):
    note = get_object_or_404(Note, pk=pk)
    
    # Check if user is the author
    if note.author != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to delete this note.")
    
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Note deleted successfully!')
        return redirect('notes:note_list')
    
    return render(request, 'notes/note_delete.html', {'note': note})
