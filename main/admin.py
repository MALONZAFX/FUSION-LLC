from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.safestring import mark_safe
import json

from .models import (
    SiteSettings, HeroImage, AboutSection, Service,
    ImpactResult, GalleryImage, Testimonial,
    NewsletterContent, ContactSubmission, NewsletterSubscription,
    FormSubmission, SystemLog
)

# ============ ADMIN SITE CONFIG ============
admin.site.site_header = "FUSION-FORCE LLC ADMIN"
admin.site.site_title = "Fusion Force Administration"
admin.site.index_title = "Welcome to Fusion Force Dashboard"

# ============ CUSTOM ADMIN ACTIONS ============
def make_active(modeladmin, request, queryset):
    queryset.update(is_active=True)
    messages.success(request, f"{queryset.count()} items marked as active")
make_active.short_description = "✅ Mark selected as active"

def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)
    messages.success(request, f"{queryset.count()} items marked as inactive")
make_inactive.short_description = "❌ Mark selected as inactive"

def duplicate_items(modeladmin, request, queryset):
    for obj in queryset:
        obj.pk = None
        obj.title = f"{obj.title} (Copy)"
        obj.save()
    messages.success(request, f"{queryset.count()} items duplicated")
duplicate_items.short_description = "📋 Duplicate selected items"

def export_as_json(modeladmin, request, queryset):
    import json
    from django.http import HttpResponse
    data = []
    for obj in queryset:
        data.append({
            'id': obj.id,
            'title': str(obj),
            'created': obj.created_at.isoformat() if hasattr(obj, 'created_at') else None
        })
    response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="export.json"'
    return response
export_as_json.short_description = "📤 Export selected as JSON"

# ============ CUSTOM ADMIN FILTERS ============
class ActiveFilter(admin.SimpleListFilter):
    title = 'Active Status'
    parameter_name = 'is_active'
    
    def lookups(self, request, model_admin):
        return (
            ('active', 'Active'),
            ('inactive', 'Inactive'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(is_active=True)
        if self.value() == 'inactive':
            return queryset.filter(is_active=False)

# ============ SITE SETTINGS ADMIN ============
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'logo_preview', 'contact_email', 'contact_phone', 'updated_at_display']
    list_display_links = ['site_name']
    readonly_fields = ['created_at', 'updated_at', 'logo_preview_large']
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: contain; background: #f0f0f0; padding: 5px; border-radius: 5px;" />', 
                obj.logo.url
            )
        return format_html('<div style="width: 50px; height: 50px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 5px;">No Logo</div>')
    logo_preview.short_description = 'Logo'
    
    def logo_preview_large(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px; object-fit: contain; background: #f0f0f0; padding: 10px; border-radius: 10px; border: 1px solid #ddd;" />', 
                obj.logo.url
            )
        return "No logo uploaded"
    logo_preview_large.short_description = 'Logo Preview'
    
    def updated_at_display(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d %H:%M')
    updated_at_display.short_description = 'Last Updated'
    
    fieldsets = (
        ('Site Information', {
            'fields': ('site_name', 'logo', 'logo_preview_large'),
            'classes': ('wide',)
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse', 'wide')
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one SiteSettings object
        return SiteSettings.objects.count() == 0

# ============ HERO IMAGE ADMIN ============
@admin.register(HeroImage)
class HeroImageAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'title', 'position_display', 'order', 'is_active_badge', 'created_at_display']
    list_filter = ['position', ActiveFilter, 'created_at']
    list_editable = ['order']  # FIXED: Removed 'title' from list_editable
    list_display_links = ['title']  # ADDED: Make title clickable
    search_fields = ['title']
    actions = [make_active, make_inactive, duplicate_items]
    readonly_fields = ['created_at', 'image_preview_large']
    list_per_page = 20
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 40px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />', 
                obj.image.url
            )
        return format_html('<div style="width: 60px; height: 40px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 4px;">No Image</div>')
    image_preview.short_description = 'Preview'
    
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 300px; object-fit: contain; border-radius: 8px; border: 2px solid #ddd;" />', 
                obj.image.url
            )
        return "No image uploaded"
    image_preview_large.short_description = 'Large Preview'
    
    def position_display(self, obj):
        color = 'blue' if obj.position == 'desktop' else 'green'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_position_display()
        )
    position_display.short_description = 'Position'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Active</span>'
            )
        return format_html(
            '<span style="background: #6c757d; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Inactive</span>'
        )
    is_active_badge.short_description = 'Status'
    
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')
    created_at_display.short_description = 'Created'
    
    fieldsets = (
        ('Hero Image Details', {
            'fields': ('title', 'image', 'image_preview_large', 'position'),
            'classes': ('wide',)
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active'),
            'classes': ('wide',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse', 'wide')
        }),
    )

# ============ ABOUT SECTION ADMIN ============
@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'image_preview', 'is_active_badge', 'created_at_display', 'updated_at_display']
    list_display_links = ['title']  # FIXED: Added list_display_links
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at', 'image_preview_large', 'bullet_points_preview']
    actions = [make_active, make_inactive, duplicate_items]
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />', 
                obj.image.url
            )
        return format_html('<div style="width: 50px; height: 50px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 4px;">No Image</div>')
    image_preview.short_description = 'Image'
    
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 300px; object-fit: contain; border-radius: 8px; border: 2px solid #ddd;" />', 
                obj.image.url
            )
        return "No image uploaded"
    image_preview_large.short_description = 'Large Preview'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Active</span>'
            )
        return format_html(
            '<span style="background: #6c757d; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Inactive</span>'
        )
    is_active_badge.short_description = 'Status'
    
    def bullet_points_preview(self, obj):
        if obj.bullet_points_list:
            html = '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6;">'
            html += '<h4 style="margin-top: 0; color: #053e91;">Bullet Points Preview:</h4>'
            html += '<ul style="margin-bottom: 0;">'
            for point in obj.bullet_points_list:
                html += f'<li style="margin-bottom: 5px;">{point}</li>'
            html += '</ul></div>'
            return format_html(html)
        return "No bullet points defined"
    bullet_points_preview.short_description = 'Preview'
    
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')
    created_at_display.short_description = 'Created'
    
    def updated_at_display(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d %H:%M')
    updated_at_display.short_description = 'Updated'
    
    fieldsets = (
        ('About Content', {
            'fields': ('title', 'content', 'image', 'image_preview_large'),
            'classes': ('wide',)
        }),
        ('Bullet Points', {
            'fields': ('bullet_points', 'bullet_points_preview'),
            'description': 'Enter each bullet point on a new line. They will appear in the about section.',
            'classes': ('wide',)
        }),
        ('Status', {
            'fields': ('is_active',),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse', 'wide')
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one AboutSection object
        return AboutSection.objects.count() == 0

# ============ SERVICE ADMIN ============
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['icon_preview', 'title', 'service_type_display', 'button_text', 'order', 'is_active_badge', 'created_at_display']
    list_filter = ['service_type', ActiveFilter, 'created_at']
    list_editable = ['order', 'button_text']  # FIXED: Only editable fields that are in list_display
    list_display_links = ['title']  # ADDED: Make title clickable
    search_fields = ['title', 'description', 'topics']
    actions = [make_active, make_inactive, duplicate_items]
    readonly_fields = ['created_at', 'updated_at', 'topics_preview']
    list_per_page = 20
    
    def icon_preview(self, obj):
        if obj.icon:
            return format_html(
                '<i class="{} fa-lg" style="color: #053e91;"></i>',
                obj.icon
            )
        return format_html('<div style="width: 30px; height: 30px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 4px;">No Icon</div>')
    icon_preview.short_description = 'Icon'
    
    def service_type_display(self, obj):
        colors = {
            'keynote': '#28a745',
            'training': '#007bff',
            'sales': '#6f42c1'
        }
        color = colors.get(obj.service_type, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color,
            obj.get_service_type_display()
        )
    service_type_display.short_description = 'Type'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Active</span>'
            )
        return format_html(
            '<span style="background: #6c757d; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Inactive</span>'
        )
    is_active_badge.short_description = 'Status'
    
    def topics_preview(self, obj):
        if obj.topics_list:
            html = '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6;">'
            html += '<h4 style="margin-top: 0; color: #053e91;">Topics Preview:</h4>'
            for topic in obj.topics_list:
                html += f'<span style="display: inline-block; background: white; color: #053e91; padding: 4px 12px; margin: 3px; border-radius: 20px; border: 1px solid #053e91; font-size: 13px;">{topic}</span> '
            html += '</div>'
            return format_html(html)
        return "No topics defined"
    topics_preview.short_description = 'Topics Preview'
    
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')
    created_at_display.short_description = 'Created'
    
    fieldsets = (
        ('Service Information', {
            'fields': ('title', 'service_type', 'description'),
            'classes': ('wide',)
        }),
        ('Display Settings', {
            'fields': ('icon', 'topics', 'topics_preview', 'button_text'),
            'description': 'For topics, separate with commas. For icon, use Font Awesome classes like "fas fa-microphone"',
            'classes': ('wide',)
        }),
        ('Order & Status', {
            'fields': ('order', 'is_active'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse', 'wide')
        }),
    )

# ============ IMPACT RESULT ADMIN ============
@admin.register(ImpactResult)
class ImpactResultAdmin(admin.ModelAdmin):
    list_display = ['value', 'title', 'order', 'is_active_badge', 'created_at_display']
    list_display_links = ['title']
    list_filter = [ActiveFilter, 'created_at']
    list_editable = ['value', 'order']  # FIXED: 'value' is in list_display
    search_fields = ['title', 'value']
    actions = [make_active, make_inactive, duplicate_items]
    readonly_fields = ['created_at']
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Active</span>'
            )
        return format_html(
            '<span style="background: #6c757d; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Inactive</span>'
        )
    is_active_badge.short_description = 'Status'
    
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')
    created_at_display.short_description = 'Created'
    
    fieldsets = (
        ('Impact Result', {
            'fields': ('title', 'value'),
            'classes': ('wide',)
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active'),
            'classes': ('wide',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse', 'wide')
        }),
    )

# ============ GALLERY IMAGE ADMIN ============
@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'title', 'position_display', 'order', 'is_active_badge', 'created_at_display']
    list_filter = ['position', ActiveFilter, 'created_at']
    list_editable = ['order']  # FIXED: Removed 'position' from list_editable
    list_display_links = ['title']  # ADDED: Make title clickable
    search_fields = ['title', 'description']
    actions = [make_active, make_inactive, duplicate_items]
    readonly_fields = ['created_at', 'updated_at', 'image_preview_large']
    list_per_page = 20
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 40px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />', 
                obj.image.url
            )
        return format_html('<div style="width: 60px; height: 40px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 4px;">No Image</div>')
    image_preview.short_description = 'Preview'
    
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 300px; object-fit: contain; border-radius: 8px; border: 2px solid #ddd;" />', 
                obj.image.url
            )
        return "No image uploaded"
    image_preview_large.short_description = 'Large Preview'
    
    def position_display(self, obj):
        colors = {
            'large': '#dc3545',
            'small': '#17a2b8',
            'tall': '#28a745'
        }
        color = colors.get(obj.position, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color,
            obj.get_position_display()
        )
    position_display.short_description = 'Position'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Active</span>'
            )
        return format_html(
            '<span style="background: #6c757d; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Inactive</span>'
        )
    is_active_badge.short_description = 'Status'
    
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')
    created_at_display.short_description = 'Created'
    
    fieldsets = (
        ('Gallery Image Details', {
            'fields': ('title', 'image', 'image_preview_large', 'description', 'position'),
            'classes': ('wide',)
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse', 'wide')
        }),
    )

# ============ TESTIMONIAL ADMIN ============
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['avatar_preview', 'client_name', 'company', 'position', 'order', 'is_active_badge', 'created_at_display']
    list_filter = ['is_active', 'company', 'created_at']
    list_editable = ['order']  # FIXED: Removed other fields from list_editable
    list_display_links = ['client_name']  # ADDED: Make client_name clickable
    search_fields = ['client_name', 'company', 'position', 'content']
    actions = [make_active, make_inactive, duplicate_items]
    readonly_fields = ['created_at', 'updated_at', 'avatar_preview_large']
    list_per_page = 20
    
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 50%; border: 2px solid #053e91;" />', 
                obj.avatar.url
            )
        return format_html(
            '<div style="width: 40px; height: 40px; background: #f0f0f0; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #053e91; font-weight: bold; font-size: 14px;">{}</div>',
            obj.client_name[:2].upper() if obj.client_name else "??"
        )
    avatar_preview.short_description = 'Avatar'
    
    def avatar_preview_large(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width: 150px; height: 150px; object-fit: cover; border-radius: 50%; border: 3px solid #053e91;" />', 
                obj.avatar.url
            )
        return format_html(
            '<div style="width: 150px; height: 150px; background: #f0f0f0; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #053e91; font-weight: bold; font-size: 24px; border: 3px solid #053e91;">{}</div>',
            obj.client_name[:2].upper() if obj.client_name else "??"
        )
    avatar_preview_large.short_description = 'Large Preview'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Active</span>'
            )
        return format_html(
            '<span style="background: #6c757d; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Inactive</span>'
        )
    is_active_badge.short_description = 'Status'
    
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')
    created_at_display.short_description = 'Created'
    
    fieldsets = (
        ('Client Information', {
            'fields': ('client_name', 'position', 'company'),
            'classes': ('wide',)
        }),
        ('Testimonial Content', {
            'fields': ('content', 'avatar', 'avatar_preview_large'),
            'description': 'Avatar should be a square image (e.g., 300x300 pixels)',
            'classes': ('wide',)
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse', 'wide')
        }),
    )

# ============ NEWSLETTER CONTENT ADMIN ============
@admin.register(NewsletterContent)
class NewsletterContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'image_preview', 'pdf_preview', 'is_active_badge', 'created_at_display', 'updated_at_display']
    list_display_links = ['title']  # FIXED: Added list_display_links
    search_fields = ['title', 'subtitle']
    readonly_fields = ['created_at', 'updated_at', 'image_preview_large', 'benefits_preview', 'pdf_link']
    actions = [make_active, make_inactive]
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />', 
                obj.image.url
            )
        return format_html('<div style="width: 50px; height: 50px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 4px;">No Image</div>')
    image_preview.short_description = 'Image'
    
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 300px; object-fit: contain; border-radius: 8px; border: 2px solid #ddd;" />', 
                obj.image.url
            )
        return "No image uploaded"
    image_preview_large.short_description = 'Large Preview'
    
    def pdf_preview(self, obj):
        if obj.pdf_file:
            return format_html(
                '<a href="{}" target="_blank" style="background: #dc3545; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px; text-decoration: none;">📄 View PDF</a>',
                obj.pdf_file.url
            )
        return format_html(
            '<span style="background: #6c757d; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">No PDF</span>'
        )
    pdf_preview.short_description = 'PDF'
    
    def pdf_link(self, obj):
        if obj.pdf_file:
            return format_html(
                '<a href="{}" target="_blank" class="button">Open PDF in new tab</a>',
                obj.pdf_file.url
            )
        return "No PDF uploaded"
    pdf_link.short_description = 'PDF Link'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Active</span>'
            )
        return format_html(
            '<span style="background: #6c757d; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Inactive</span>'
        )
    is_active_badge.short_description = 'Status'
    
    def benefits_preview(self, obj):
        if obj.benefits_list:
            html = '<div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #dee2e6;">'
            html += '<h4 style="margin-top: 0; color: #053e91;">Benefits Preview (Two Columns):</h4>'
            html += '<div style="column-count: 2; column-gap: 30px;">'
            for benefit in obj.benefits_list:
                html += f'<div style="margin-bottom: 10px; break-inside: avoid;">'
                html += f'<span style="color: #28a745; margin-right: 8px;">✓</span> {benefit}'
                html += '</div>'
            html += '</div></div>'
            return format_html(html)
        return "No benefits defined"
    benefits_preview.short_description = 'Benefits Preview'
    
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')
    created_at_display.short_description = 'Created'
    
    def updated_at_display(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d %H:%M')
    updated_at_display.short_description = 'Updated'
    
    fieldsets = (
        ('Newsletter Content', {
            'fields': ('title', 'subtitle', 'image', 'image_preview_large'),
            'classes': ('wide',)
        }),
        ('Benefits List', {
            'fields': ('benefits', 'benefits_preview'),
            'description': 'Add each benefit on a new line. They will be displayed in two columns on the website.',
            'classes': ('wide',)
        }),
        ('PDF File', {
            'fields': ('pdf_file', 'pdf_link'),
            'description': 'Upload newsletter PDF for download. Max file size: 10MB',
            'classes': ('wide',)
        }),
        ('Status', {
            'fields': ('is_active',),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse', 'wide')
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one NewsletterContent object
        return NewsletterContent.objects.count() == 0

# ============ CONTACT SUBMISSION ADMIN ============
@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'organization', 'event_type', 'status', 'submitted_at']
    list_filter = ['status', 'event_type', 'submitted_at']
    list_editable = ['status']  # NOW IT'S IN list_display
    list_display_links = ['id']  # Make ID clickable
    search_fields = ['full_name', 'email', 'organization', 'event_details']
    readonly_fields = ['submitted_at', 'contacted_at', 'event_details_display']
    date_hierarchy = 'submitted_at'
    actions = ['mark_as_contacted', 'mark_as_booked', 'mark_as_cancelled']
    list_per_page = 25
    
    def event_details_display(self, obj):
        return format_html(
            '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6; white-space: pre-wrap; max-height: 300px; overflow: auto;">{}</div>',
            obj.event_details
        )
    event_details_display.short_description = 'Event Details'
    
    def mark_as_contacted(self, request, queryset):
        updated = queryset.update(status='contacted', contacted_at=timezone.now())
        messages.success(request, f"{updated} submissions marked as contacted")
    mark_as_contacted.short_description = "📞 Mark selected as contacted"
    
    def mark_as_booked(self, request, queryset):
        updated = queryset.update(status='booked')
        messages.success(request, f"{updated} submissions marked as booked")
    mark_as_booked.short_description = "✅ Mark selected as booked"
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        messages.success(request, f"{updated} submissions marked as cancelled")
    mark_as_cancelled.short_description = "❌ Mark selected as cancelled"
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('full_name', 'email', 'organization'),
            'classes': ('wide',)
        }),
        ('Event Details', {
            'fields': ('event_type', 'event_details_preview'),
            'classes': ('wide',)
        }),
        ('Status & Follow-up', {
            'fields': ('status', 'contacted_at', 'notes'),
            'classes': ('wide',)
        }),
        ('Submission Time', {
            'fields': ('submitted_at',),
            'classes': ('collapse', 'wide')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data and obj.status == 'contacted':
            obj.contacted_at = timezone.now()
        super().save_model(request, obj, form, change)
# ============ NEWSLETTER SUBSCRIPTION ADMIN ============
@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    # Use actual field names from your model
    list_display = ['email', 'name', 'source', 'is_active', 'subscribed_at_display']
    list_filter = ['source', 'is_active']  # Removed submitted_at from list_filter
    # list_editable = ['is_active']  # REMOVED FOR NOW - fix list_display first
    list_display_links = ['email']
    search_fields = ['email', 'name']
    # readonly_fields = ['submitted_at']  # REMOVED - check if field exists
    # date_hierarchy = 'submitted_at'  # REMOVED - check if field exists
    actions = [make_active, make_inactive, 'export_emails']
    list_per_page = 50
    
    # Custom method for source (if you want badges)
    def source_display(self, obj):
        colors = {
            'newsletter_section': '#28a745',
            'footer': '#17a2b8'
        }
        color = colors.get(obj.source, '#6c757d')
        display_text = dict(obj.SOURCE_CHOICES).get(obj.source, obj.source)
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color,
            display_text
        )
    source_display.short_description = 'Source'
    
    # Custom method for status
    def status_display(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Active</span>'
            )
        return format_html(
            '<span style="background: #6c757d; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Inactive</span>'
        )
    status_display.short_description = 'Status'
    
    # Check what date field your model actually has
    def subscribed_at_display(self, obj):
        # Try different possible field names
        date_field = None
        
        # Check common date field names
        if hasattr(obj, 'created_at'):
            date_field = obj.created_at
        elif hasattr(obj, 'submitted_at'):
            date_field = obj.submitted_at
        elif hasattr(obj, 'date_joined'):
            date_field = obj.date_joined
        elif hasattr(obj, 'timestamp'):
            date_field = obj.timestamp
        
        if date_field:
            return date_field.strftime('%Y-%m-%d %H:%M')
        return 'N/A'
    subscribed_at_display.short_description = 'Subscribed'
    
    def export_emails(self, request, queryset):
        emails = list(queryset.values_list('email', flat=True))
        email_list = '\n'.join(emails)
        response = HttpResponse(email_list, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="newsletter_emails.txt"'
        return response
    export_emails.short_description = "📧 Export selected emails"
    
    # Simplified fieldsets - adjust based on actual model fields
    fieldsets = (
        ('Subscriber Information', {
            'fields': ('name', 'email', 'source'),
            'classes': ('wide',)
        }),
        ('Status', {
            'fields': ('is_active', 'agreed_to_terms'),
            'classes': ('wide',)
        }),
    )
    
    # Add this method to check what fields your model has
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Debug: print available fields
        print("Available fields in model:", [f.name for f in self.model._meta.get_fields()])
        return form

# ============ FORM SUBMISSION ADMIN ============
@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = ['source_badge', 'submitted_at_display', 'processed_display', 'form_data_preview']  # FIXED: Changed to processed_display
    list_filter = ['source', 'processed', 'submitted_at']
    list_editable = []  # FIXED: Empty list_editable
    list_display_links = ['source_badge']  # ADDED: Make source_badge clickable
    search_fields = ['source', 'form_data']
    readonly_fields = ['submitted_at', 'form_data_display']
    date_hierarchy = 'submitted_at'
    actions = ['mark_as_processed', 'mark_as_unprocessed']
    list_per_page = 25
    
    def source_badge(self, obj):
        colors = {
            'booking': '#dc3545',
            'newsletter': '#28a745',
            'footer': '#17a2b8'
        }
        color = colors.get(obj.source, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color,
            obj.get_source_display()
        )
    source_badge.short_description = 'Source'
    
    def processed_display(self, obj):  # FIXED: Renamed from processed_badge
        if obj.processed:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Processed</span>'
            )
        return format_html(
            '<span style="background: #ffc107; color: black; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Pending</span>'
        )
    processed_display.short_description = 'Status'
    
    def submitted_at_display(self, obj):
        return obj.submitted_at.strftime('%Y-%m-%d %H:%M')
    submitted_at_display.short_description = 'Submitted'
    
    def form_data_preview(self, obj):
        try:
            data = json.loads(obj.form_data)
            preview = json.dumps(data, indent=2)[:80] + '...' if len(json.dumps(data)) > 80 else json.dumps(data, indent=2)
            return format_html(
                '<pre style="margin: 0; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; background: #f8f9fa; padding: 5px; border-radius: 4px; font-size: 11px;">{}</pre>',
                preview
            )
        except:
            return "Invalid JSON"
    form_data_preview.short_description = 'Form Data'
    
    def form_data_display(self, obj):
        try:
            data = json.loads(obj.form_data)
            formatted = json.dumps(data, indent=2)
            return format_html(
                '<pre style="background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6; max-height: 500px; overflow: auto;">{}</pre>',
                formatted
            )
        except:
            return "Invalid JSON"
    form_data_display.short_description = 'Form Data (Full)'
    
    def mark_as_processed(self, request, queryset):
        updated = queryset.update(processed=True)
        messages.success(request, f"{updated} submissions marked as processed")
    mark_as_processed.short_description = "✅ Mark selected as processed"
    
    def mark_as_unprocessed(self, request, queryset):
        updated = queryset.update(processed=False)
        messages.success(request, f"{updated} submissions marked as unprocessed")
    mark_as_unprocessed.short_description = "⏳ Mark selected as unprocessed"
    
    fieldsets = (
        ('Submission Information', {
            'fields': ('source', 'processed'),
            'classes': ('wide',)
        }),
        ('Form Data', {
            'fields': ('form_data_display',),
            'classes': ('wide',)
        }),
        ('Timestamp', {
            'fields': ('submitted_at',),
            'classes': ('collapse', 'wide')
        }),
    )
    
    def has_add_permission(self, request):
        return False

# ============ SYSTEM LOG ADMIN ============
@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ['log_level_badge', 'message_truncated', 'source', 'created_at_display']
    list_filter = ['log_level', 'source', 'created_at']
    search_fields = ['message', 'source']
    readonly_fields = ['created_at', 'user_ip', 'user_agent', 'full_message']
    date_hierarchy = 'created_at'
    actions = ['clear_old_logs']
    list_per_page = 50
    
    def log_level_badge(self, obj):
        color_map = {
            'info': '#17a2b8',
            'warning': '#ffc107',
            'error': '#dc3545',
            'success': '#28a745'
        }
        color = color_map.get(obj.log_level, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">{}</span>',
            color,
            obj.get_log_level_display().upper()
        )
    log_level_badge.short_description = 'Level'
    
    def message_truncated(self, obj):
        if len(obj.message) > 80:
            return f"{obj.message[:80]}..."
        return obj.message
    message_truncated.short_description = 'Message'
    
    def full_message(self, obj):
        return format_html(
            '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6; white-space: pre-wrap; font-family: monospace;">{}</div>',
            obj.message
        )
    full_message.short_description = 'Full Message'
    
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
    created_at_display.short_description = 'Created'
    
    def clear_old_logs(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta
        
        # Delete logs older than 30 days
        cutoff_date = timezone.now() - timedelta(days=30)
        old_logs = SystemLog.objects.filter(created_at__lt=cutoff_date)
        count = old_logs.count()
        old_logs.delete()
        messages.success(request, f"Cleared {count} logs older than 30 days")
    clear_old_logs.short_description = "🗑️ Clear logs older than 30 days"
    
    fieldsets = (
        ('Log Details', {
            'fields': ('log_level', 'message', 'full_message', 'source'),
            'classes': ('wide',)
        }),
        ('User Information', {
            'fields': ('user_ip', 'user_agent'),
            'classes': ('collapse', 'wide')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse', 'wide')
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False