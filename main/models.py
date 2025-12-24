from django.db import models

# ============ SITE SETTINGS ============
class SiteSettings(models.Model):
    logo = models.ImageField(upload_to='site/', blank=True, null=True)
    site_name = models.CharField(max_length=100, default='Fusion Force LLC')
    contact_email = models.EmailField(default='info@fusionforce.com')
    contact_phone = models.CharField(max_length=20, default='+1 (443) 545-4565')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.site_name

    class Meta:
        verbose_name_plural = "Site Settings"

# ============ HERO SECTION ============
class HeroImage(models.Model):
    POSITION_CHOICES = [
        ('desktop', 'Desktop Hero'),
        ('mobile', 'Mobile Hero'),
    ]
    
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='hero/')
    position = models.CharField(max_length=10, choices=POSITION_CHOICES, default='desktop')
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_position_display()})"

# ============ ABOUT SECTION ============
class AboutSection(models.Model):
    title = models.CharField(max_length=200, default='Pamela Robinson')
    content = models.TextField(default='Pamela Robinson is a keynote speaker, corporate and leadership trainer, founder of Fusion Force and a recognized expert in sales and marketing support for hospitality companies.')
    image = models.ImageField(upload_to='about/', blank=True, null=True)
    bullet_points = models.TextField(
        default="Keynote Speaker\nLeadership Trainer\nHospitality Expert\nGlobal Experience",
        help_text="Enter each bullet point on a new line"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def bullet_points_list(self):
        if self.bullet_points:
            return [point.strip() for point in self.bullet_points.split('\n') if point.strip()]
        return []

    def __str__(self):
        return self.title

# ============ SERVICES SECTION ============
class Service(models.Model):
    SERVICE_TYPES = [
        ('keynote', 'Keynote Speaking'),
        ('training', 'Corporate Training'),
        ('sales', 'Sales & Marketing Support'),
    ]
    
    title = models.CharField(max_length=200)
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES)
    description = models.TextField()
    icon = models.CharField(
        max_length=100, 
        help_text="Font Awesome icon class (e.g., fas fa-microphone)",
        default='fas fa-star'
    )
    topics = models.TextField(
        help_text="Enter topics separated by commas",
        default="Topic 1, Topic 2, Topic 3"
    )
    button_text = models.CharField(max_length=50, default='Learn More')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def topics_list(self):
        if self.topics:
            return [topic.strip() for topic in self.topics.split(',') if topic.strip()]
        return []

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

# ============ IMPACT RESULTS ============
class ImpactResult(models.Model):
    title = models.CharField(max_length=200)
    value = models.CharField(max_length=50, help_text="e.g., 25%, 100+, etc.")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.value} - {self.title}"

# ============ GALLERY SECTION ============
class GalleryImage(models.Model):
    GALLERY_POSITION_CHOICES = [
        ('large', 'Large (Top Horizontal)'),
        ('small', 'Small (3 in Row)'),
        ('tall', 'Tall (Right Vertical)'),
    ]
    
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='gallery/')
    description = models.TextField(blank=True)
    position = models.CharField(max_length=10, choices=GALLERY_POSITION_CHOICES, default='small')
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_position_display()})"

# ============ TESTIMONIALS SECTION ============
class Testimonial(models.Model):
    client_name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    content = models.TextField()
    avatar = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.client_name} - {self.company}"

# ============ NEWSLETTER SECTION ============
class NewsletterContent(models.Model):
    title = models.CharField(max_length=200, default="Monthly Newsletter")
    subtitle = models.CharField(max_length=300, default="Get exclusive insights and industry updates delivered to your inbox")
    image = models.ImageField(upload_to='newsletter/', blank=True, null=True)
    benefits = models.TextField(
        default="Leadership Strategies\nIndustry Updates\nCase Studies\nEvent Announcements\nExclusive Content\nSuccess Stories",
        help_text="Add each benefit on a new line. They will be displayed in two columns."
    )
    pdf_file = models.FileField(upload_to='newsletter_pdfs/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def benefits_list(self):
        if self.benefits:
            return [benefit.strip() for benefit in self.benefits.split('\n') if benefit.strip()]
        return []

    class Meta:
        verbose_name = "Newsletter Content"
        verbose_name_plural = "Newsletter Content"

    def __str__(self):
        return f"Newsletter Content - {self.updated_at.strftime('%Y-%m-%d')}"

# ============ FORM SUBMISSIONS ============
class ContactSubmission(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled'),
    ]
    
    EVENT_TYPE_CHOICES = [
        ('keynote', 'Keynote Speech'),
        ('workshop', 'Workshop'),
        ('training', 'Corporate Training'),
        ('consultation', 'Consultation'),
    ]
    
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    organization = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    event_details = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    submitted_at = models.DateTimeField(auto_now_add=True)
    contacted_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.full_name} - {self.organization} ({self.event_type})"


class NewsletterSubscription(models.Model):
    SOURCE_CHOICES = [
        ('newsletter_section', 'Newsletter Section'),
        ('footer', 'Footer'),
    ]
    
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default='footer')
    is_active = models.BooleanField(default=True)
    agreed_to_terms = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = "Newsletter Subscription"
        verbose_name_plural = "Newsletter Subscriptions"

# ============ NEW FORM SUBMISSION FOR FORMSPREE ============
class FormSubmission(models.Model):
    SOURCE_CHOICES = [
        ('booking', 'Booking Form'),
        ('newsletter', 'Newsletter Form'),
        ('footer', 'Footer Newsletter'),
    ]
    
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    form_data = models.JSONField()  # Store all form data from FormSubmit
    submitted_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.source} - {self.submitted_at.strftime('%Y-%m-%d %H:%M')}"

# ============ SYSTEM LOGS ============
class SystemLog(models.Model):
    LOG_LEVELS = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('success', 'Success'),
    ]
    
    log_level = models.CharField(max_length=20, choices=LOG_LEVELS, default='info')
    message = models.TextField()
    source = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_log_level_display()} - {self.source} - {self.created_at}"