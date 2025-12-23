from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
import json
import logging
from django.db import IntegrityError

from .models import (
    SiteSettings, HeroImage, AboutSection, Service,
    ImpactResult, GalleryImage, Testimonial,
    NewsletterContent, ContactSubmission, NewsletterSubscription,
    SystemLog
)

logger = logging.getLogger(__name__)

def log_system_action(message, level='info', source='views', request=None):
    """Helper to log system actions"""
    try:
        SystemLog.objects.create(
            log_level=level,
            message=message,
            source=source,
            user_ip=request.META.get('REMOTE_ADDR', '') if request else '',
            user_agent=request.META.get('HTTP_USER_AGENT', '') if request else ''
        )
    except Exception as e:
        logger.error(f"Failed to log action: {e}")
        
def home(request):
    """Main home view - with aggressive cache prevention"""
    try:
        # Debug - print to console on EVERY request
        print("\n" + "="*80)
        print(f"[DEBUG] Home view called at: {timezone.now()}")
        
        # Get all data
        site_settings = SiteSettings.objects.first()
        hero_images = HeroImage.objects.filter(is_active=True).order_by('order')
        about_section = AboutSection.objects.filter(is_active=True).first()
        services = Service.objects.filter(is_active=True).order_by('order')
        results = ImpactResult.objects.filter(is_active=True).order_by('order')
        gallery_images = GalleryImage.objects.filter(is_active=True).order_by('order')[:6]
        testimonials = Testimonial.objects.filter(is_active=True).order_by('order')
        newsletter = NewsletterContent.objects.filter(is_active=True).first()
        
        # ADD DEBUG PRINT
        print(f"\n🔥 DEBUG DATA:")
        print(f"Hero Images: {hero_images.count()}")
        print(f"About Section: {about_section}")
        print(f"Services: {services.count()}")
        print(f"Gallery Images: {gallery_images.count()}")
        
        context = {
            'site_settings': site_settings,
            'hero_images': hero_images,
            'about_section': about_section,
            'services': services,
            'results': results,
            'gallery_images': gallery_images,
            'testimonials': testimonials,
            'newsletter': newsletter,
        }
        
        response = render(request, 'main/index.html', context)
        
       # ADD THESE LINES FOR PRODUCTION:
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
    
        return response
        
        
        
    except Exception as e:
        print(f"[ERROR] in home view: {str(e)}")
        import traceback
        traceback.print_exc()
        return render(request, 'main/index.html', {})

@csrf_exempt
@require_POST
def contact_submit(request):
    """Handle contact form submission - SAVES TO DJANGO DATABASE"""
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['full_name', 'email', 'organization', 'event_type', 'event_details']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'status': 'error',
                    'message': f'{field.replace("_", " ").title()} is required.'
                }, status=400)
        
        # Create contact submission in Django database
        submission = ContactSubmission.objects.create(
            full_name=data['full_name'],
            email=data['email'],
            organization=data['organization'],
            event_type=data['event_type'],
            event_details=data['event_details']
        )
        
        # Log the submission
        log_system_action(
            f"New contact submission from {submission.full_name} ({submission.organization})",
            level='success',
            source='contact_form',
            request=request
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Thank you for your booking request! Pamela will review your details and get back to you within 24 hours.',
            'submission_id': submission.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request data.'
        }, status=400)
    except Exception as e:
        log_system_action(
            f"Contact submission error: {str(e)}",
            level='error',
            source='contact_form',
            request=request
        )
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred. Please try again later.'
        }, status=500)

@csrf_exempt
@require_POST
def newsletter_submit(request):
    """Handle newsletter subscription - SAVES TO DJANGO DATABASE"""
    try:
        data = json.loads(request.body)
        
        email = data.get('email', '').strip()
        name = data.get('name', '').strip()
        source = data.get('source', 'newsletter_section')
        agreed_to_terms = data.get('agreed_to_terms', True)
        
        if not email:
            return JsonResponse({
                'status': 'error',
                'message': 'Email is required.'
            }, status=400)
        
        # Check if email already exists
        if NewsletterSubscription.objects.filter(email=email).exists():
            subscription = NewsletterSubscription.objects.get(email=email)
            return JsonResponse({
                'status': 'info',
                'message': f'You are already subscribed to our newsletter! (Subscribed on {subscription.created_at.strftime("%Y-%m-%d")})'
            })
        
        # Create subscription in Django database
        subscription = NewsletterSubscription.objects.create(
            email=email,
            name=name if name else email.split('@')[0],
            source=source,
            agreed_to_terms=agreed_to_terms,
            is_active=True
        )
        
        # Log the subscription
        log_system_action(
            f"New newsletter subscription: {email}",
            level='success',
            source='newsletter_form',
            request=request
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Thank you for subscribing to our newsletter!',
            'subscription_id': subscription.id
        })
        
    except IntegrityError:
        return JsonResponse({
            'status': 'info',
            'message': 'You are already subscribed to our newsletter!'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request data.'
        }, status=400)
    except Exception as e:
        log_system_action(
            f"Newsletter subscription error: {str(e)}",
            level='error',
            source='newsletter_form',
            request=request
        )
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred. Please try again later.'
        }, status=500)

@csrf_exempt
@require_POST
def form_submit_webhook(request):
    """Webhook to receive form submissions from FormSubmit (optional backup)"""
    try:
        data = json.loads(request.body)
        
        # This is a backup in case JavaScript fails
        # You can process FormSubmit data here if needed
        
        log_system_action(
            f"FormSubmit webhook received: {data.get('_subject', 'Unknown')}",
            level='info',
            source='formsubmit_webhook',
            request=request
        )
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        log_system_action(
            f"FormSubmit webhook error: {str(e)}",
            level='error',
            source='formsubmit_webhook',
            request=request
        )
        return JsonResponse({'status': 'error'}, status=500)

