from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage, send_mail
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import SignUpForm, LoginForm
from .models import CustomUser
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                
                # Generate confirmation token
                token = default_token_generator.make_token(user)
                current_site = get_current_site(request)
                mail_subject = 'Activate your MU_demia account'
                
                # Prepare email content
                context = {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': token,
                }
                message = render_to_string('accounts/email_verification.html', context)
                
                try:
                    # Try sending email using send_mail first
                    send_mail(
                        mail_subject,
                        message,
                        None,  # Use DEFAULT_FROM_EMAIL from settings
                        [user.email],
                        fail_silently=False,
                    )
                    return render(request, 'accounts/verification_sent.html')
                    
                except Exception as email_error:
                    logger.error(f"Failed to send verification email: {str(email_error)}")
                    # If send_mail fails, try using EmailMessage
                    try:
                        email = EmailMessage(
                            mail_subject,
                            message,
                            to=[user.email]
                        )
                        email.send(fail_silently=False)
                        return render(request, 'accounts/verification_sent.html')
                        
                    except Exception as backup_error:
                        logger.error(f"Backup email method failed: {str(backup_error)}")
                        user.delete()
                        messages.error(request, 'Failed to send verification email. Please check your email settings or try again later.')
                        return redirect('accounts:signup')
                        
            except Exception as e:
                logger.error(f"Error during signup process: {str(e)}")
                messages.error(request, 'An error occurred during signup. Please try again.')
                return redirect('accounts:signup')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True  # Enable login after email verification
        user.is_email_verified = True
        user.save()
        login(request, user)
        messages.success(request, 'Your email has been verified successfully!')
        return redirect('core:home')
    else:
        return render(request, 'accounts/verification_invalid.html')

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(email=email, password=password)
            
            if user is not None:
                if user.is_email_verified:
                    login(request, user)
                    messages.success(request, 'You have been logged in successfully!')
                    return redirect('core:home')
                else:
                    return render(request, 'accounts/verification_required.html', {'email': email})
            else:
                form.add_error(None, 'Invalid email or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@require_http_methods(["POST"])
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect(reverse('core:home'))  # Use reverse() to generate the correct URL

@require_http_methods(["POST"])
def resend_verification(request):
    email = request.POST.get('email')
    try:
        user = CustomUser.objects.get(email=email)
        if not user.is_email_verified:
            token = default_token_generator.make_token(user)
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('accounts/email_verification.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': token,
            })
            email = EmailMessage(mail_subject, message, to=[user.email])
            email.send()
            messages.success(request, 'Verification email has been resent.')
        else:
            messages.info(request, 'This email is already verified.')
    except CustomUser.DoesNotExist:
        messages.error(request, 'No account found with this email address.')
    
    return redirect('accounts:login')